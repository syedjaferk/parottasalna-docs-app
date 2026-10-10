# Session 9 · VPC Peering

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/3d-BvgVd4G4"
  title="Session 9: VPC peering" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 9** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=3d-BvgVd4G4)

## What you'll learn

- Why companies end up with **many VPCs**, and what **VPC peering** does
- The peering **lifecycle**: request, accept, routes, security groups
- The rules that matter: **no overlapping CIDRs**, **not transitive**, **no edge-to-edge routing**
- **Cross-account** and **inter-Region** peering (the Sydney ↔ Mumbai class lab)
- **DNS** across peered VPCs
- When to use peering vs Transit Gateway vs PrivateLink

```{raw} html
:file: ../diagrams/s09-peering.html
```

## 1. Why many VPCs, and what peering is

**🧑 In plain words.** Two separate office buildings, each with its own security. **Peering** builds
a **private footbridge** between them, so staff walk across directly instead of going out onto the street.

**❓ The problem it solves.** Teams separate environments (prod/dev), business units or acquired
companies into different VPCs and accounts for safety and billing. But some systems must still talk
privately: an app in one VPC calling a shared database or a monitoring server in another, without
the internet, VPN or public IPs.

**⚙️ How it works.** A peering connection (`pcx-…`) is a **one-to-one** networking link between two
VPCs over the AWS backbone. There's no gateway device, no single point of failure and no bandwidth
bottleneck. Instances use **private IPs** across it. It works within an account, **across accounts**
and **across Regions** (inter-Region traffic is encrypted automatically).

**💡 Example.** A company keeps a `shared-services` VPC (Jenkins, monitoring, LDAP) and peers it with
`prod` and `staging` so both can be monitored and deployed to privately.

## 2. The peering lifecycle

**🧑 In plain words.** One building **proposes** the bridge, the other **agrees**, then both put up
**signboards** pointing to it, and both guards add the other building's staff to their allowed list.

**❓ The problem it solves.** Making sure both owners consent and both sides know the path; missing
any one step is the most common reason peering "doesn't work".

**⚙️ How it works.**

1. **Request:** VPC A's owner creates the peering, naming VPC B (account ID and Region if different).
2. **Accept:** VPC B's owner accepts within 7 days (status *pending-acceptance* → *active*).
3. **Routes on both sides:** A's route table `10.1.0.0/16 → pcx-…`; B's route table `10.0.0.0/16 → pcx-…`.
   You can route the whole peer CIDR or just some subnets.
4. **Security groups / NACLs:** allow the peer's traffic. In the **same Region** you can reference
   the peer VPC's **security group ID**; across Regions, use **CIDRs**.
5. **Optional DNS:** enable *DNS resolution from accepter/requester VPC* so the peer's **private DNS
   names** (`ip-10-1-1-20.ap-south-1.compute.internal`) resolve to private IPs.

**💡 Example.** Peering is *active* and routes exist, but ping fails: the target's security group
doesn't allow ICMP from `10.0.0.0/16`. Step 4 was skipped.

## 3. The rules (exam favourites)

**🧑 In plain words.** Footbridges have **strict rules**: the two buildings can't share flat numbers;
a bridge only joins **two** buildings; and you can't use the neighbour's main gate to go out.

**❓ The problem it solves.** Knowing the limits tells you when peering is the wrong tool.

**⚙️ How it works.**

| Rule | Meaning | Consequence |
|---|---|---|
| **No overlapping CIDRs** | `10.0.0.0/16` can't peer with another `10.0.0.0/16` (or any overlap) | plan IP ranges company-wide, early |
| **Not transitive** | A↔B + B↔C does **not** give A↔C | every pair that must talk needs its own peering |
| **No edge-to-edge routing** | A can't use B's **IGW, NAT Gateway, VPN, Direct Connect** or gateway endpoint | shared internet/VPN access needs Transit Gateway |
| **One peering per pair** | n VPCs in a full mesh need **n(n−1)/2** connections | 10 VPCs = 45 peerings, each with routes |
| **Limits** | 50 active peerings per VPC by default (raisable to 125) | large meshes hit limits |
| **Cost** | **no hourly fee**; normal data transfer charges (cross-AZ / inter-Region) | cheapest way to link a few VPCs |

**💡 Example.** VPC B has a NAT Gateway. VPC A's private instances route `0.0.0.0/0` to the peering
hoping to use B's NAT: it doesn't work (no edge-to-edge routing).

## 4. Cross-account and inter-Region peering

**🧑 In plain words.** Footbridges between buildings owned by **different companies**, or a
**private tunnel between cities**.

**❓ The problem it solves.** Mergers, partner integrations and multi-Region architectures need
private connectivity beyond one account or Region.

**⚙️ How it works.**

- **Cross-account:** the requester enters the other **account ID** and VPC ID; the other account
  accepts in its console. Each side controls its own routes and security groups.
- **Inter-Region:** choose *Another Region*, then **accept in the other Region's console**. Traffic
  stays on the AWS backbone and is **encrypted**. Security groups must use **CIDRs** (no SG
  references across Regions). Data transfer between Regions is charged.

**💡 Example (class lab).** VPC A in **Sydney** (`10.0.0.0/16`) peers with VPC B in **Mumbai**
(`10.1.0.0/16`); an EC2 in Sydney pings the Mumbai instance's private IP over the AWS network.

## 5. Hands-on: peer two VPCs

Create `vpc-a` (`10.0.0.0/16`) and `vpc-b` (`10.1.0.0/16`), each with a subnet and an instance.

1. *VPC → Peering connections → Create*: requester `vpc-a`, accepter `vpc-b` → **Accept request**.
2. Route tables:

   ```text
   vpc-a route table:  10.1.0.0/16 → pcx-0123abcd
   vpc-b route table:  10.0.0.0/16 → pcx-0123abcd
   ```

3. Security group on instance B: allow ICMP (ping) from `10.0.0.0/16`.
4. From instance A:

```bash
ping -c 3 10.1.1.20
```

**Output:**

```text
64 bytes from 10.1.1.20: icmp_seq=1 ttl=127 time=0.62 ms
64 bytes from 10.1.1.20: icmp_seq=2 ttl=127 time=0.55 ms
64 bytes from 10.1.1.20: icmp_seq=3 ttl=127 time=0.58 ms
```

### The class lab: across two Regions

In class we peered **Sydney** (`ap-southeast-2`, VPC A `10.0.0.0/16`) with **Mumbai**
(`ap-south-1`, VPC B `10.1.0.0/16`). The steps are the same, with three differences:

- Create the peering from the Sydney console, choose **Another Region** → `ap-south-1` and paste VPC
  B's ID; then **accept it in the Mumbai console** (switch Region).
- Security groups can't reference the other Region's security group: allow the **CIDR** (`10.0.0.0/16`).
- Traffic between Regions is encrypted automatically and billed as inter-Region data transfer.

## 6. Peering vs Transit Gateway vs PrivateLink

| Need | Best fit |
|---|---|
| A few VPCs talking to each other, cheap, simple | **VPC peering** |
| Many VPCs + on-premises, central control, transitive routing | **Transit Gateway** ([Session 10](10-transit-gateway.md)) |
| Expose **one service** (not the whole network) to other VPCs, even with overlapping CIDRs | **PrivateLink** / interface endpoints ([Session 11](11-vpc-endpoints.md)) |

## Common mistakes

- **Adding the route on only one side.** Traffic goes out but replies have no way back.
- **Overlapping CIDRs** discovered too late: peering is then impossible; renumbering is painful.
- **Expecting A to reach C through B.** It never will with peering.
- **Expecting the peer's NAT/IGW to work for you.** No edge-to-edge routing.

## Hands-on exercises

Peering connections are **free** (you pay data transfer). ⚠️ EC2 instances cost money; use small
instances and terminate them at the end.

**Exercise 1 · Two VPCs.** Create `vpc-a` (`10.0.0.0/16`) and `vpc-b` (`10.1.0.0/16`), each with one
subnet and a small instance. Note both private IPs.

<details class="solution"><summary>Check</summary>

Two VPCs with non-overlapping CIDRs; `aws ec2 describe-instances --query 'Reservations[].Instances[].PrivateIpAddress'`
lists `10.0.x.x` and `10.1.x.x`.

</details>

**Exercise 2 · Request and accept.** Create the peering `vpc-a → vpc-b` and accept it.

<details class="solution"><summary>CLI</summary>

```bash
PCX=$(aws ec2 create-vpc-peering-connection --vpc-id $VPC_A --peer-vpc-id $VPC_B \
      --query VpcPeeringConnection.VpcPeeringConnectionId --output text)
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $PCX
```

</details>

**Exercise 3 · Ping before routes.** With the peering *active* but no routes yet, ping B from A. Why does it fail?

<details class="solution"><summary>Answer</summary>

A's route table has no route for `10.1.0.0/16`, so packets never use the peering.

</details>

**Exercise 4 · One-sided routes.** Add the route **only in A's** route table and ping again. Explain the result.

<details class="solution"><summary>Answer</summary>

Still fails: requests reach B, but B has no route back to `10.0.0.0/16`, so replies are lost. Add
`10.0.0.0/16 → pcx` in B's route table too.

</details>

**Exercise 5 · Security group referencing.** Allow ICMP on B's instance using **A's security group ID**
as the source (same Region), then ping.

<details class="solution"><summary>Check</summary>

Inbound rule: *All ICMP – IPv4*, source `sg-…` (A's SG; the console accepts peered-VPC SGs in the
same Region). `ping -c 3 10.1.1.x` works.

</details>

**Exercise 6 · Private DNS across the peering.** Enable *DNS resolution* on the peering (both
directions) and DNS hostnames in both VPCs. From A, resolve B's private DNS name.

<details class="solution"><summary>Check</summary>

`dig +short ip-10-1-1-20.ap-south-1.compute.internal` from A returns `10.1.1.20`.

</details>

**Exercise 7 · Prove non-transitivity.** Create `vpc-c` (`10.2.0.0/16`) peered with B only. From A,
try to reach C, even after adding a route `10.2.0.0/16 → pcx-ab` in A.

<details class="solution"><summary>Answer</summary>

It fails: peering isn't transitive, and B won't forward A's traffic to C. Fix: peer A↔C directly, or use a Transit Gateway.

</details>

**Exercise 8 · Overlap is refused.** Create `vpc-d` with `10.0.0.0/16` (same as A) and try to peer it with A.

<details class="solution"><summary>Expected</summary>

The peering goes to **failed** with *overlapping CIDR* (or can't be created). Overlapping VPCs can never be peered.

</details>

**Exercise 9 · No edge-to-edge.** Give B a NAT Gateway; in A's private route table point
`0.0.0.0/0` at the peering. Can A reach the internet through B? ⚠️ Delete the NAT right after.

<details class="solution"><summary>Answer</summary>

No. The route can be added, but B drops traffic that arrives over the peering and is headed for
its NAT Gateway: **edge-to-edge routing isn't supported**.

</details>

**Exercise 10 · Inter-Region (class lab).** Peer a VPC in **Sydney** (`ap-southeast-2`) with one in
**Mumbai**. Accept it in the Mumbai console, add routes and CIDR-based SG rules, and ping across.
Note the round-trip time.

<details class="solution"><summary>What to notice</summary>

Acceptance happens in the **other Region's** console. Ping works with ~100+ ms (Sydney↔Mumbai
distance). Security group rules must use the CIDR, not the SG ID.

</details>

**Exercise 11 · Mesh maths.** How many peerings for full meshes of 4, 8 and 20 VPCs? At which point
would you switch to a Transit Gateway?

<details class="solution"><summary>Answer</summary>

4 → 6, 8 → 28, 20 → 190. Beyond a handful of VPCs (or as soon as you need shared VPN/internet
access or central control), use a Transit Gateway.

</details>

**Exercise 12 · Clean up.** Delete the peering connections (routes pointing at them become
*blackhole*), remove those routes, terminate instances, and delete the VPCs in **both Regions**.

<details class="solution"><summary>Check</summary>

VPC → Peering connections: all *deleted*. No running instances in either Region.

</details>
