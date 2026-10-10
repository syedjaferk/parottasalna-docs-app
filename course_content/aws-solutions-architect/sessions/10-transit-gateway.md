# Session 10 · Transit Gateway

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/MPNMrl6IkgM"
  title="Session 10: Transit Gateway" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 10** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=MPNMrl6IkgM)

## The big idea

Peering every VPC with every other VPC turns into spaghetti: 10 VPCs need 45 peerings, each with
its own routes. A **Transit Gateway (TGW)** is a **central hub router**: each VPC, VPN or Direct
Connect link attaches **once**, and the hub's route tables decide who can reach whom. Unlike
peering, routing through the hub **is transitive**.

**Everyday example:** a city bus terminal. Instead of a direct bus between every pair of towns,
every route goes to the central terminal and you change there. Add a new town = add one route to
the terminal.

```{raw} html
:file: ../diagrams/s10-tgw.html
```

## 1. Key pieces

| Piece | Meaning |
|---|---|
| **Transit Gateway** | the regional hub router (scales to thousands of attachments) |
| **Attachment** | a connection to the hub: **VPC**, **Site-to-Site VPN**, **Direct Connect gateway**, **TGW peering** (another Region or account), Connect (SD-WAN) |
| **TGW route table** | which attachment a destination CIDR goes to |
| **Association** | each attachment uses exactly one TGW route table for its outgoing lookups |
| **Propagation** | an attachment automatically adds its CIDRs to a route table |

A VPC attachment places a network interface in **one subnet per AZ** you choose. Your VPC route
tables then send other networks' traffic to the TGW, e.g. `10.0.0.0/8 → tgw-…`.

## 2. Transit Gateway vs VPC peering

| | VPC peering | Transit Gateway |
|---|---|---|
| Topology | point-to-point mesh | hub and spoke |
| Transitive routing | ❌ | ✅ |
| On-premises (VPN / Direct Connect) | ❌ (no edge-to-edge) | ✅ attach once, shared by all VPCs |
| Segmentation | per peering | **multiple route tables**: e.g. dev can't reach prod, both reach shared |
| Cost | no hourly fee, data transfer only | **per attachment per hour + per GB processed** |
| Best for | a handful of VPCs | many VPCs, hybrid networks, central control |

## 3. Segmentation with route tables

A common design: `prod` and `dev` must both reach `shared` (CI, DNS, monitoring) but **never each other**.

| TGW route table | Associated with | Routes (propagated from) |
|---|---|---|
| `rt-prod` | prod attachment | shared |
| `rt-dev` | dev attachment | shared |
| `rt-shared` | shared attachment | prod, dev |

## 4. Hands-on: three VPCs through one hub

1. Create three VPCs, as in class: **developer** `10.1.0.0/16`, **testing** `10.2.0.0/16` and **production** `10.3.0.0/16` (non-overlapping!), each with one subnet and an instance.
2. *VPC → Transit gateways → Create* (keep *default route table association/propagation* on for the simple lab).
3. *Transit gateway attachments → Create* one **VPC attachment** per VPC.
4. In each VPC's route table add `10.0.0.0/8 → tgw-…`.
5. From the developer instance (e.g. `10.1.1.150`), ping the testing and production instances: both work, through one hub.
6. Then try the segmentation from section 3: give **production** its own TGW route table so developer can no longer reach it.

```bash
aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id tgw-rtb-0abc \
    --filters Name=type,Values=propagated --query 'Routes[].DestinationCidrBlock'
```

**Output:**

```text
[ "10.1.0.0/16", "10.2.0.0/16", "10.3.0.0/16" ]
```

**Clean up:** delete the attachments (billed per hour), then the Transit Gateway.

## Common mistakes

- **Forgetting the VPC-side route** to the TGW: the hub knows the way, but the VPC doesn't send traffic there.
- **Overlapping CIDRs** between attached VPCs: routes collide.
- **Attachment subnets in only one AZ:** instances in other AZs can't use the attachment. Pick a subnet in every AZ you use.
- **Leaving lab attachments running.**

## Try it yourself

1. A company has 30 VPCs and two offices with VPNs; every VPC must reach both offices. Peering or Transit Gateway?

   <details class="solution">
   <summary>Answer</summary>

   **Transit Gateway**: attach the 30 VPCs and the 2 VPNs once. Peering can't share a VPN across
   VPCs (no edge-to-edge routing) and would need 435 peerings for a full mesh.

   </details>

2. How do you stop `dev` from reaching `prod` while both reach `shared` through one TGW?

   <details class="solution">
   <summary>Answer</summary>

   Use separate TGW route tables: associate dev and prod with tables that only contain the shared
   VPC's routes, and associate shared with a table that has both.

   </details>
