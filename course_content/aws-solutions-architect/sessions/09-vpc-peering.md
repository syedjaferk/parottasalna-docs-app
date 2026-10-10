# Session 9 · VPC Peering

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/3d-BvgVd4G4"
  title="Session 9: VPC peering" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 9** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=3d-BvgVd4G4)

## The big idea

Companies end up with many VPCs: prod, dev, a shared-services VPC, a partner's account. **VPC
peering** joins **two** VPCs privately over the AWS network, so their instances talk using private IPs,
as if on one network, with no internet, VPN or gateway in between.

**Everyday example:** a private footbridge between two buildings. People cross directly without
going out onto the street. But a bridge from A to B and one from B to C doesn't let you walk from A
to C through B's offices.

```{raw} html
:file: ../diagrams/s09-peering.html
```

## 1. How it works

1. VPC A **requests** a peering connection (`pcx-…`) to VPC B.
2. VPC B's owner **accepts** it (same account, another account, or another Region).
3. **Both sides add routes**: A's route table `10.1.0.0/16 → pcx-…`, B's `10.0.0.0/16 → pcx-…`.
4. **Security groups** allow the traffic. In the same Region you can reference the peer VPC's
   security group; across Regions, use CIDR ranges.

## 2. The rules (exam favourites)

| Rule | Meaning |
|---|---|
| **No overlapping CIDRs** | `10.0.0.0/16` can't peer with another `10.0.0.0/16`. Plan IP ranges early! |
| **Not transitive** | A↔B + B↔C does **not** give A↔C |
| **No edge-to-edge routing** | A can't use B's Internet Gateway, NAT Gateway, VPN or Direct Connect |
| **One peering per pair** | n VPCs fully meshed need n(n−1)/2 connections: 10 VPCs = 45 |
| Cross-account and inter-Region | supported; inter-Region traffic is encrypted |
| Cost | no hourly charge; you pay normal data transfer |

## 3. Hands-on: peer two VPCs

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

## 4. Peering vs Transit Gateway vs PrivateLink

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

## Try it yourself

1. You have 5 VPCs that must all reach each other. How many peering connections do you need?

   <details class="solution">
   <summary>Answer</summary>

   5 × 4 / 2 = **10**.

   </details>

2. The peering connection is *Active* and both route tables are correct, but ping still fails.
   What's left to check?

   <details class="solution">
   <summary>Answer</summary>

   The **security group** of the target instance (allow ICMP from the other VPC's CIDR or SG) and the **NACLs** on both subnets.

   </details>
