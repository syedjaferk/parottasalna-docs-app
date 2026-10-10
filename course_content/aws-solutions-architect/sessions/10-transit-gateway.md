# Session 10 · Transit Gateway

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/MPNMrl6IkgM"
  title="Session 10: Transit Gateway" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 10** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=MPNMrl6IkgM)

## What you'll learn

- The **"peering spaghetti"** problem and the hub-and-spoke answer
- Transit Gateway pieces: **attachments**, **route tables**, **associations**, **propagations**
- **Transitive routing** and **segmentation** (dev can't reach prod)
- Connecting **on-premises** networks with VPN / Direct Connect
- **Inter-Region** and **cross-account** Transit Gateways
- Transit Gateway vs VPC peering, and the cost model

```{raw} html
:file: ../diagrams/s10-tgw.html
```

## 1. Hub-and-spoke networking

**🧑 In plain words.** A **city bus terminal**. Instead of a direct bus between every pair of
towns, every route goes to the central terminal, and you change there. Adding a new town means
adding **one** route to the terminal, not one to every other town.

**❓ The problem it solves.** With peering, 10 VPCs need 45 connections, each with routes on both
sides; peering isn't transitive; and peered VPCs can't share one VPN or Direct Connect link. Growth
turns into unmanageable spaghetti.

**⚙️ How it works.** A **Transit Gateway (TGW)** is a **regional, highly available virtual router**
managed by AWS. Networks **attach** to it once. The TGW forwards traffic between attachments
according to **its own route tables**, so routing through the hub **is transitive**. It scales to
thousands of attachments and up to 100 Gbps per VPC attachment (burst).

**💡 Example.** A company with 25 VPCs and 3 offices attaches all 28 networks to one TGW. Any VPC can
reach any office through the hub, and a new VPC needs one attachment.

## 2. Attachments

**🧑 In plain words.** Each **bus route** that connects a town to the terminal.

**❓ The problem it solves.** Different kinds of networks must plug into the same hub.

**⚙️ How it works.**

| Attachment | Connects |
|---|---|
| **VPC** | a VPC; you choose **one subnet per AZ** where the TGW places a network interface |
| **Site-to-Site VPN** | an office/data centre over IPsec tunnels (supports ECMP for more bandwidth) |
| **Direct Connect gateway** | a private dedicated line to on-premises |
| **TGW peering** | another TGW in another Region (or account) |
| **Connect** | SD-WAN appliances (GRE + BGP) |

Inside each VPC, **your VPC route tables** must send traffic for other networks to the TGW, e.g.
`10.0.0.0/8 → tgw-…`. Use dedicated small subnets (e.g. `/28`) for attachments, one per AZ.

**💡 Example.** Instances in AZ c can't reach other VPCs: the VPC attachment only has subnets in
AZ a and b. Add an attachment subnet in AZ c.

## 3. TGW route tables, associations and propagations

**🧑 In plain words.** The terminal's **departure boards**. Each incoming route is told **which
board** to read (association), and each town **posts its own name** on chosen boards (propagation).

**❓ The problem it solves.** Not every network should reach every other. You need central,
explicit control of who talks to whom.

**⚙️ How it works.**

- A TGW can have **several route tables**.
- **Association:** each attachment is associated with **exactly one** TGW route table. When traffic
  *arrives from* that attachment, the TGW looks up the destination in that table.
- **Propagation:** an attachment can **automatically add its CIDRs** as routes into one or more
  route tables (VPNs/DX propagate BGP-learned routes too).
- **Static routes** can be added by hand, including **blackhole** routes to drop traffic.
- By default a new TGW has one default route table with association and propagation on (full mesh).

**💡 Example (segmentation).** `prod` and `dev` must both reach `shared`, but never each other:

| TGW route table | Associated attachments | Routes (propagated from) |
|---|---|---|
| `rt-prod` | prod | shared |
| `rt-dev` | dev | shared |
| `rt-shared` | shared | prod, dev |

Dev's lookups happen in `rt-dev`, which has no route to prod, so dev → prod is impossible.

## 4. On-premises and inter-Region

**🧑 In plain words.** The terminal also has a **link to the highway** (the office network) and a
**train line to the terminal in another city** (another Region).

**❓ The problem it solves.** Hybrid companies need every VPC to reach the data centre, without one VPN per VPC.

**⚙️ How it works.** Attach **one** Site-to-Site VPN or Direct Connect gateway to the TGW; with route
propagation (BGP), every VPC learns the office routes and the office learns the VPC CIDRs.
**TGW peering** links hubs in different Regions over the AWS backbone (encrypted, static routes).
Share a TGW with other accounts through **AWS Resource Access Manager (RAM)**, so one network team
runs a central hub for the whole organisation.

**💡 Example.** Mumbai TGW (10 VPCs + office VPN) peers with the Singapore TGW (5 VPCs). A Singapore
app reaches the Chennai office via Singapore TGW → Mumbai TGW → VPN.

## 5. Transit Gateway vs VPC peering

| | VPC peering | Transit Gateway |
|---|---|---|
| Topology | point-to-point mesh | hub and spoke |
| Transitive routing | ❌ | ✅ |
| On-premises (VPN / Direct Connect) | ❌ (no edge-to-edge) | ✅ attach once, shared by all VPCs |
| Segmentation | per peering | **multiple route tables**, blackhole routes |
| Latency | lowest (direct) | an extra hop (tiny) |
| Cost | no hourly fee, data transfer only | **per attachment per hour + per GB processed** |
| Best for | a handful of VPCs, cost-sensitive, high bandwidth pairs | many VPCs, hybrid networks, central control |

Many companies use **both**: a TGW for general connectivity, plus a direct peering for one very
high-traffic pair to save processing charges.

## 6. Hands-on: three VPCs through one hub

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

## Hands-on exercises

⚠️ Transit Gateway attachments cost money **per hour**, plus per GB. Do these in one sitting and
delete the attachments and the TGW at the end. Use three small instances.

**Exercise 1 · Three VPCs (class lab).** Create **developer** `10.1.0.0/16`, **testing**
`10.2.0.0/16` and **production** `10.3.0.0/16`, each with one subnet and an instance.

<details class="solution"><summary>Check</summary>

Three non-overlapping VPCs; note each instance's private IP (e.g. `10.1.1.150`, `10.2.1.x`, `10.3.1.x`).

</details>

**Exercise 2 · Create the TGW.** Create a Transit Gateway with default route table association and propagation **enabled**.

<details class="solution"><summary>CLI</summary>

```bash
TGW=$(aws ec2 create-transit-gateway --description lab \
      --options DefaultRouteTableAssociation=enable,DefaultRouteTablePropagation=enable \
      --query TransitGateway.TransitGatewayId --output text)
aws ec2 describe-transit-gateways --transit-gateway-ids $TGW --query 'TransitGateways[].State'
```

Wait for `available`.

</details>

**Exercise 3 · Attach the VPCs.** Create a VPC attachment for each VPC (pick the instance's subnet).

<details class="solution"><summary>CLI</summary>

```bash
aws ec2 create-transit-gateway-vpc-attachment --transit-gateway-id $TGW --vpc-id $VPC_DEV --subnet-ids $SUBNET_DEV
# repeat for testing and production
```

</details>

**Exercise 4 · Ping without VPC routes.** Ping production from developer. Why does it fail?

<details class="solution"><summary>Answer</summary>

The TGW knows all three CIDRs, but the **VPC route tables** don't send `10.x` traffic to the TGW.
Each VPC needs a route like `10.0.0.0/8 → tgw-…`.

</details>

**Exercise 5 · Add VPC routes and ping.** Add `10.0.0.0/8 → tgw-…` to all three VPC route tables,
allow ICMP from `10.0.0.0/8` in the security groups, and ping all pairs.

<details class="solution"><summary>Check</summary>

Every instance can ping the other two through one hub: transitive routing works.

</details>

**Exercise 6 · Read the TGW route table.** List the routes in the default TGW route table. Which are
*propagated*?

<details class="solution"><summary>CLI</summary>

```bash
aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id <tgw-rtb> \
    --filters Name=state,Values=active --query 'Routes[].[DestinationCidrBlock,Type]' --output table
```

All three `10.x.0.0/16` routes, type **propagated**.

</details>

**Exercise 7 · Segment production.** Make developer unable to reach production while testing still
reaches both. Use a new TGW route table.

<details class="solution"><summary>One way</summary>

Create `rt-dev`; **disassociate** developer from the default table and associate it with `rt-dev`;
in `rt-dev` propagate only **testing**. Developer's lookups now have no route to `10.3.0.0/16`, so
pings to production fail, while testing still reaches both.

</details>

**Exercise 8 · Blackhole route.** Instead of segmentation, add a **static blackhole** route for
`10.3.0.0/16` in the developer's TGW route table. What's the difference from simply not having the route?

<details class="solution"><summary>Answer</summary>

Same visible effect (dropped), but a blackhole is **explicit** and wins over a broader route (e.g. a
`10.0.0.0/8` to a firewall), so it documents intent and blocks reliably.

</details>

**Exercise 9 · AZ coverage.** Launch a fourth instance in developer VPC's **other AZ** without adding a
subnet from that AZ to the attachment. Can it reach testing? Fix it.

<details class="solution"><summary>Answer</summary>

No: the attachment has no interface in that AZ. Modify the attachment and add a subnet in the second AZ.

</details>

**Exercise 10 · Flow through the hub.** Enable **TGW Flow Logs** (or VPC Flow Logs on the attachment
ENIs) and find the developer → testing pings.

<details class="solution"><summary>Where</summary>

VPC → Transit gateways → *Flow logs* tab → Create (CloudWatch Logs). Records show source `10.1.x.x`,
destination `10.2.x.x`, protocol 1 (ICMP), ACCEPT.

</details>

**Exercise 11 · Cost comparison.** Using the Pricing Calculator, compare a month of: (a) 3 VPCs
fully peered, (b) 3 VPC attachments on a TGW, each with 50 GB/month between VPCs. When does TGW win anyway?

<details class="solution"><summary>What to conclude</summary>

Peering is cheaper on price alone. TGW wins on **operations** when you have many VPCs, need
transitive routing, shared VPN/Direct Connect, or segmentation.

</details>

**Exercise 12 · Design question.** 15 VPCs in three accounts plus two offices; security wants all
traffic to the internet to pass a central firewall VPC. Sketch the TGW design.

<details class="solution"><summary>Model answer</summary>

One TGW shared with all accounts via **RAM**. VPC attachments for all 15 VPCs and an **inspection
VPC** (firewalls/GWLB with NAT). VPN attachments for the offices. Spoke route tables send
`0.0.0.0/0` to the inspection VPC attachment; the inspection route table propagates all spokes.
Separate route tables to keep prod and dev apart.

</details>

**Exercise 13 · Clean up.** Delete the VPC attachments (wait for *deleted*), then the TGW route
tables, then the TGW, then instances and VPCs.

<details class="solution"><summary>Check</summary>

VPC → Transit gateway attachments: none in *available* state. Billing for TGW stops once attachments are gone.

</details>
