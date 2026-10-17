# Chapter 59 · Peer-to-peer (P2P) architecture

## The big idea

In **peer-to-peer**, there is **no central server**. Every participant (a **peer**) is both a **client and a
server**: it **requests** resources from others and **provides** resources to others. The capacity of the
system **grows with the number of users**.

**Everyday example:** a **village well versus a city water company**. The company (client-server) has one
plant; if it breaks, the whole city is dry, and more customers need a bigger plant. With neighbours sharing
buckets from their own wells (P2P), everybody both uses and supplies water, there is no single plant to fail,
and more neighbours means more wells.

```{raw} html
:file: ../diagrams/p2p.html
```

## Client-server vs P2P

| | Client-server | Peer-to-peer |
|---|---|---|
| Roles | Fixed: client asks, server serves | **Every node is both** |
| Control | Central | **Decentralised** |
| Scaling | Buy bigger / more servers | **More peers add capacity** |
| Cost to the operator | Servers and bandwidth | Mostly borne by the peers |
| Failure | Server is a SPOF | Survives many peer failures |
| Trust and security | One trusted authority | Peers are **untrusted** |
| Search and consistency | Easy (central database) | Hard |
| Examples | Web, email, banking | BitTorrent, blockchains, Skype (early), IPFS |

## Three kinds of P2P

### 1. Centralised (hybrid) P2P

A **central index server** knows who has what, but **the data flows directly between peers**. Napster worked
this way. Easy search; the index is a SPOF and legal target.

### 2. Unstructured P2P

Peers connect **randomly**. To find a file you **flood** the query to neighbours (Gnutella). No central
point, but search is **expensive and unreliable** (cannot guarantee finding rare items).

### 3. Structured P2P (DHT)

Peers organise themselves so each key has a **well-defined owner**, found in **O(log N)** hops. The most
important idea: the **Distributed Hash Table (DHT)** (Chord, Kademlia, Pastry).

## How a DHT finds data

Give every peer and every key an **id on a ring** (like consistent hashing). A key is owned by the peer whose id
is its **successor**. Each peer only knows a few others (a "finger table" with entries 1, 2, 4, 8, 16... steps
around the ring), so every hop **halves** the remaining distance.

```python
import hashlib

BITS = 8
RING = 2 ** BITS

def node_id(name):
    return int(hashlib.sha1(name.encode()).hexdigest(), 16) % RING

peers = sorted({node_id(f"peer{i}") for i in range(20)})

def successor(key):
    for p in peers:
        if p >= key:
            return p
    return peers[0]                                   # wrap around the ring

def in_open(x, a, b):
    """True if x lies strictly between a and b going clockwise around the ring."""
    return (a < x < b) if a < b else (x > a or x < b)

def route(start, key):
    """Chord-style lookup: always jump to the farthest finger that does not overshoot the key."""
    owner = successor(key)
    hops, current = [start], start
    while current != owner:
        nxt = owner
        for finger in reversed([successor((current + 2 ** i) % RING) for i in range(BITS)]):
            if in_open(finger, current, key):
                nxt = finger
                break
        hops.append(nxt)
        current = nxt
    return hops

key = node_id("song.mp3")
path = route(peers[0], key)
print(f"20 peers on a {RING}-slot ring. Key 'song.mp3' hashes to {key}, owned by peer {successor(key)}")
print("lookup path from peer", peers[0], ":", " -> ".join(map(str, path)), f"({len(path) - 1} hops)")
```

**Output:**

```text
20 peers on a 256-slot ring. Key 'song.mp3' hashes to 84, owned by peer 103
lookup path from peer 18 : 18 -> 50 -> 69 -> 72 -> 103 (4 hops)
```

A lookup in a network of millions of peers takes only **about 20 hops** (log2 of the size). That is how
BitTorrent's DHT, IPFS and Ethereum's discovery find things without a central directory.

## Real systems

| System | What peers do |
|---|---|
| **BitTorrent** | Share file pieces; each downloader also uploads. A **tracker** or the **DHT** finds peers. Popular files download faster. |
| **Bitcoin / Ethereum** | Every node holds the ledger copy, validates blocks, gossips transactions; **consensus** (proof of work/stake) replaces a central bank |
| **IPFS** | Content-addressed file sharing (files are found by their **hash**) |
| **WebRTC** | Browsers send video/audio **directly** to each other (a signalling server only introduces them) |
| **Skype (originally), Hangouts** | Calls routed peer-to-peer where possible |
| **Windows Update delivery, game patchers** | Neighbouring machines share downloads |
| **Cassandra, Dynamo (internally)** | Nodes are **peers** in a ring (no master), though clients talk to them as servers |

## Strengths and challenges

| Strengths | Challenges |
|---|---|
| **No single point of failure**, resilient | **Finding** things (search) is harder |
| **Scales with users**: demand adds supply | Peers **join and leave constantly** (churn) |
| Low infrastructure cost for the operator | **Security**: any peer may be malicious (fake data, Sybil attacks, eclipse attacks) |
| Censorship-resistant | **NAT and firewalls** block incoming connections (need hole punching, relays) |
| Uses spare bandwidth at the edge | **Consistency** and agreement are hard (needs consensus or accepts eventual) |
| | Free riders (downloading without sharing); hard to monitor and update |

## Designing with P2P in mind

- **Verify everything:** never trust data from a peer. Use **hashes** (content addressing) and **signatures**.
  BitTorrent checks every piece's hash.
- **Incentives:** BitTorrent's **tit-for-tat** gives faster downloads to peers who upload.
- **Handling NAT:** **STUN/TURN/ICE** (WebRTC) and relays so peers behind routers can connect.
- **Bootstrapping:** a new peer needs at least one known peer or a **seed/bootstrap node**.
- **Hybrid designs are common:** a central server for **discovery or login**, P2P for the **heavy data**
  (video calls, large downloads), to get the best of both.

## Common mistakes

:::{warning}
- Trusting data from peers without verification.
- Assuming peers are always online and well connected.
- Designing without a bootstrap and NAT-traversal plan.
- Using P2P where a simple client-server design (and a CDN) would be easier and more reliable.
:::

## Try it yourself

1. Why does BitTorrent become faster for a popular file, while a normal web download becomes slower?
2. Why must a P2P system verify the hash of every piece it receives?
3. A DHT has 1 million peers. About how many hops does a lookup take?

<details class="solution"><summary>Answers</summary>

1. Every downloader also **uploads**, so more users add more supply. A central server's bandwidth is shared among more users.
2. Peers are untrusted: any one could send corrupted or malicious data. A hash lets the receiver check the piece against a known, trusted value.
3. About log2(1,000,000) = **20 hops**.

</details>

:::{admonition} Next
:class: important
We have met many options. The skill is choosing between them. Next: the [top system design
trade-offs](60-top-system-design-tradeoffs.md).
:::
