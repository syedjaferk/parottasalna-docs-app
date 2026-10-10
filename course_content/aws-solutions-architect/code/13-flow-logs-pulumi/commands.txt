aws configure                     
aws sts get-caller-identity       # confirms you're in the right account


mkdir vpc-flowlogs-demo && cd vpc-flowlogs-demo
pulumi new aws-python             # accept defaults, stack name e.g. "dev"
# replace the generated __main__.py with the one I gave you
pulumi config set aws:region ap-south-1
pulumi preview                    # dry run, should list ~20 resources
pulumi up
