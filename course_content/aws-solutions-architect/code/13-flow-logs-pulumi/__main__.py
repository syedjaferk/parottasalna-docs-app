"""
VPC Flow Logs demo - infrastructure only (flow logs are created manually in the session).

Topology
--------
Internet --(80)--> [web instance | public subnet 10.0.1.0/24] --(5000)--> [backend instance | private subnet 10.0.2.0/24]

* web      : tiny Python app on port 80 that calls the backend and renders the result
* backend  : tiny Python JSON API on port 5000 (only reachable from the web security group)
* No NAT gateway (keeps the demo cheap). Both apps use only the Python standard
  library, so nothing needs to be downloaded at boot.
* No SSH needed: the web instance has an SSM role, so use Session Manager to get a shell.
  (Optional: `pulumi config set sshCidr <your-ip>/32` to also open port 22.)
"""

import json

import pulumi
import pulumi_aws as aws

config = pulumi.Config()
instance_type = config.get("instanceType") or "t3.micro"
ssh_cidr = config.get("sshCidr")  # optional, e.g. 203.0.113.10/32

PROJECT = "vpc-flowlogs-demo"


def tags(name: str) -> dict:
    return {"Name": f"{PROJECT}-{name}", "Project": PROJECT}


# --------------------------------------------------------------------------
# Lookups
# --------------------------------------------------------------------------
azs = aws.get_availability_zones(state="available")
az = azs.names[0]

# Latest Amazon Linux 2023 (x86_64) AMI via the public SSM parameter
ami = aws.ssm.get_parameter(
    name="/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
)

# --------------------------------------------------------------------------
# Networking
# --------------------------------------------------------------------------
vpc = aws.ec2.Vpc(
    "demo-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags=tags("vpc"),
)

igw = aws.ec2.InternetGateway("demo-igw", vpc_id=vpc.id, tags=tags("igw"))

public_subnet = aws.ec2.Subnet(
    "public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone=az,
    map_public_ip_on_launch=True,
    tags=tags("public-subnet"),
)

private_subnet = aws.ec2.Subnet(
    "private-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone=az,
    map_public_ip_on_launch=False,
    tags=tags("private-subnet"),
)

public_rt = aws.ec2.RouteTable(
    "public-rt",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(cidr_block="0.0.0.0/0", gateway_id=igw.id)],
    tags=tags("public-rt"),
)
aws.ec2.RouteTableAssociation(
    "public-rta", subnet_id=public_subnet.id, route_table_id=public_rt.id
)

# Private route table: local route only (no NAT, no internet)
private_rt = aws.ec2.RouteTable("private-rt", vpc_id=vpc.id, tags=tags("private-rt"))
aws.ec2.RouteTableAssociation(
    "private-rta", subnet_id=private_subnet.id, route_table_id=private_rt.id
)

# --------------------------------------------------------------------------
# Security groups
# --------------------------------------------------------------------------
web_ingress = [
    aws.ec2.SecurityGroupIngressArgs(
        description="HTTP from anywhere",
        protocol="tcp",
        from_port=80,
        to_port=80,
        cidr_blocks=["0.0.0.0/0"],
    )
]
if ssh_cidr:
    web_ingress.append(
        aws.ec2.SecurityGroupIngressArgs(
            description="SSH from my IP",
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=[ssh_cidr],
        )
    )

allow_all_egress = [
    aws.ec2.SecurityGroupEgressArgs(
        protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"]
    )
]

web_sg = aws.ec2.SecurityGroup(
    "web-sg",
    vpc_id=vpc.id,
    description="Web tier - HTTP from the internet",
    ingress=web_ingress,
    egress=allow_all_egress,
    tags=tags("web-sg"),
)

backend_sg = aws.ec2.SecurityGroup(
    "backend-sg",
    vpc_id=vpc.id,
    description="Backend tier - port 5000 only from the web SG",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="API from web tier",
            protocol="tcp",
            from_port=5000,
            to_port=5000,
            security_groups=[web_sg.id],
        )
    ],
    egress=allow_all_egress,
    tags=tags("backend-sg"),
)

# --------------------------------------------------------------------------
# IAM: SSM access for the web instance (shell via Session Manager, no SSH needed)
# --------------------------------------------------------------------------
web_role = aws.iam.Role(
    "web-ssm-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
    tags=tags("web-ssm-role"),
)
aws.iam.RolePolicyAttachment(
    "web-ssm-attach",
    role=web_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
)
web_profile = aws.iam.InstanceProfile("web-profile", role=web_role.name)

# --------------------------------------------------------------------------
# User data
# --------------------------------------------------------------------------
BACKEND_USER_DATA = r"""#!/bin/bash
mkdir -p /opt/backend
cat > /opt/backend/app.py <<'EOF'
from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
import json
import socket


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({
            "service": "backend-api",
            "host": socket.gethostname(),
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "orders": [
                {"id": 1, "item": "Notebook", "qty": 4},
                {"id": 2, "item": "Pen", "qty": 10},
            ],
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
EOF

cat > /etc/systemd/system/backend.service <<'EOF'
[Unit]
Description=Demo backend API
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/backend/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now backend
"""

WEB_USER_DATA = r"""#!/bin/bash
mkdir -p /opt/web
cat > /opt/web/app.py <<'EOF'
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.request

BACKEND_URL = "http://__BACKEND_IP__:5000/"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with urllib.request.urlopen(BACKEND_URL, timeout=3) as r:
                data = json.dumps(json.loads(r.read()), indent=2)
            status = 200
        except Exception as e:
            data = "Backend unreachable: %s" % e
            status = 502
        body = (
            "<html><body style='font-family:sans-serif'>"
            "<h1>VPC Flow Logs Demo - Web Tier</h1>"
            "<p>Response fetched from the private backend (__BACKEND_IP__:5000):</p>"
            "<pre>%s</pre></body></html>" % data
        ).encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


HTTPServer(("0.0.0.0", 80), Handler).serve_forever()
EOF

cat > /etc/systemd/system/web.service <<'EOF'
[Unit]
Description=Demo web tier
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/web/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Helper for the demo: generates ACCEPT and REJECT flows towards the backend
cat > /opt/gen-traffic.sh <<'EOF'
#!/bin/bash
BACKEND=__BACKEND_IP__
echo "== 20 allowed requests to $BACKEND:5000 (ACCEPT) =="
for i in $(seq 1 20); do curl -s -m 2 -o /dev/null "http://$BACKEND:5000/"; done
echo "== blocked attempts to $BACKEND:8080, :22, :3306 (REJECT at backend SG) =="
for p in 8080 22 3306; do curl -s -m 2 -o /dev/null "http://$BACKEND:$p/"; done
echo done
EOF
chmod +x /opt/gen-traffic.sh

systemctl daemon-reload
systemctl enable --now web
"""

# --------------------------------------------------------------------------
# Instances
# --------------------------------------------------------------------------
backend = aws.ec2.Instance(
    "backend",
    ami=ami.value,
    instance_type=instance_type,
    subnet_id=private_subnet.id,
    vpc_security_group_ids=[backend_sg.id],
    user_data=BACKEND_USER_DATA,
    user_data_replace_on_change=True,
    metadata_options=aws.ec2.InstanceMetadataOptionsArgs(http_tokens="required"),
    tags=tags("backend"),
)

web = aws.ec2.Instance(
    "web",
    ami=ami.value,
    instance_type=instance_type,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[web_sg.id],
    associate_public_ip_address=True,
    iam_instance_profile=web_profile.name,
    user_data=backend.private_ip.apply(
        lambda ip: WEB_USER_DATA.replace("__BACKEND_IP__", ip)
    ),
    user_data_replace_on_change=True,
    metadata_options=aws.ec2.InstanceMetadataOptionsArgs(http_tokens="required"),
    tags=tags("web"),
)

# --------------------------------------------------------------------------
# Outputs (handy for the manual flow log steps)
# --------------------------------------------------------------------------
pulumi.export("vpc_id", vpc.id)
pulumi.export("public_subnet_id", public_subnet.id)
pulumi.export("private_subnet_id", private_subnet.id)
pulumi.export("web_instance_id", web.id)
pulumi.export("web_eni_id", web.primary_network_interface_id)
pulumi.export("web_public_ip", web.public_ip)
pulumi.export("web_url", web.public_ip.apply(lambda ip: f"http://{ip}"))
pulumi.export("backend_instance_id", backend.id)
pulumi.export("backend_eni_id", backend.primary_network_interface_id)
pulumi.export("backend_private_ip", backend.private_ip)
