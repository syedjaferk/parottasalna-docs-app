# Chapter 16 · Checksums

## The big idea

A **checksum** is a small value calculated from a chunk of data. If even one bit of the data changes,
the checksum (almost always) changes too. Store or send the checksum with the data; later, recompute
and compare. A mismatch means **the data got corrupted**.

**Everyday example:** the last digit of a phone number or an ISBN. A bookshop clerk who types an ISBN
wrongly gets an immediate "invalid" because the last digit no longer matches the others. No need to
look the book up.

```{raw} html
:file: ../diagrams/checksums.html
```

## Why corruption happens

Bits flip more often than people think: electrical noise on a cable, a failing disk sector, a faulty
memory chip, cosmic rays, a buggy network card. At large scale it is a daily event, not an exception.

## A family of techniques

| Technique | Detects | Strength | Used in |
|---|---|---|---|
| **Parity bit** | Any single flipped bit | Weak | Old memory, serial links |
| **Simple sum / Internet checksum** | Many accidental errors | Weak | IP, TCP, UDP headers |
| **CRC32** | Burst errors very well | Good for accidents | Ethernet, ZIP, PNG, storage blocks |
| **Cryptographic hash (SHA-256)** | Any change, even deliberate | Strong; infeasible to forge | File downloads, Git, blockchains, S3 integrity |
| **HMAC / digital signature** | Tampering **and** proves who made it | Strongest | APIs, JWTs, software updates |

## Worked example

```python
import zlib, hashlib

message = b"transfer 5000 to account 42"
checksum = zlib.crc32(message)
print("sent     :", message, hex(checksum))

corrupted = b"transfer 9000 to account 42"            # one flipped digit
print("received :", corrupted, "-> intact?", zlib.crc32(corrupted) == checksum)

print("sha256   :", hashlib.sha256(message).hexdigest()[:16], "...")
print("sha256 of corrupted:", hashlib.sha256(corrupted).hexdigest()[:16], "...")
```

**Output:**

```text
sent     : b'transfer 5000 to account 42' 0x4ca6505
received : b'transfer 9000 to account 42' -> intact? False
sha256   : 7a990de930afc219 ...
sha256 of corrupted: f682bbce834d3278 ...
```

Notice how one changed character gives a completely different hash. This **avalanche effect** is what
makes hashes useful.

## A checksum from scratch

```python
def internet_checksum(data: bytes) -> int:
    """Simplified 16-bit one's-complement checksum, as used in IP/TCP/UDP headers."""
    if len(data) % 2:
        data += b"\x00"
    total = sum(int.from_bytes(data[i:i + 2], "big") for i in range(0, len(data), 2))
    while total > 0xFFFF:
        total = (total & 0xFFFF) + (total >> 16)       # fold the carry back in
    return ~total & 0xFFFF

packet = b"HELLO NETWORKS"
c = internet_checksum(packet)
print("checksum :", hex(c))
print("valid    :", internet_checksum(packet + c.to_bytes(2, "big")) == 0)   # a correct packet sums to zero
print("tampered :", internet_checksum(b"HELLO NETWORKT" + c.to_bytes(2, "big")) == 0)
```

**Output:**

```text
checksum : 0xdf0b
valid    : True
tampered : False
```

The receiver does not even need to know the original checksum: if the data plus the checksum sum to
zero, it is intact.

## Where checksums appear in system design

- **TCP/UDP/IP:** headers carry checksums; bad packets are dropped and (for TCP) retransmitted.
- **Storage systems (HDFS, S3, ZFS, Cassandra):** every block stores a checksum. On read, a mismatch
  triggers a repair from a **replica**. This catches silent disk corruption (bit rot).
- **Downloads:** publishers list a SHA-256 so you can verify the file you got is the file they built.
- **Git:** every commit and file is named by the hash of its contents.
- **Deduplication and caching:** equal hashes mean equal content, so store once (content-addressed storage).
- **Merkle trees (Cassandra, Dynamo, blockchains):** hash the hashes. Two replicas compare **one root
  hash**; if equal, they hold identical data, if not, descend to find exactly which part differs.

## Limits: accident vs attack

A plain checksum or CRC protects against **accidents only**. An attacker who alters the data can
simply recompute the checksum. For **tampering**, use a **keyed hash (HMAC)** or **digital signature**:
only someone with the secret key can produce a valid one.

## Common mistakes

:::{warning}
- Using a plain checksum (CRC, MD5) as a security measure.
- Verifying only at the sender. Verify at the **receiver** and at **read time** too.
- Computing a checksum over the data **after** it passed through the component that corrupts it.
- Using MD5 or SHA-1 for security. Both are broken for collisions; use SHA-256.
:::

## Try it yourself

1. Why is CRC32 enough for an Ethernet frame but not for verifying a downloaded software installer?
2. Two database replicas each hold 1 TB. How can they find out cheaply whether they match?
3. What happens in a storage system when a read finds a block whose checksum is wrong?

<details class="solution"><summary>Answers</summary>

1. Ethernet errors are accidental. An installer could be modified deliberately along with its CRC, so you need a **cryptographic hash** published through a trusted channel (or a signature).
2. Build a **Merkle tree** of block hashes and compare roots. Only differing branches need to be examined.
3. The system treats the copy as corrupt, reads another replica, returns correct data and rewrites the bad block (**self-healing**).

</details>

:::{admonition} Next
:class: important
Back to names and addresses: how `shop.example.com` becomes an IP: [DNS](17-dns.md).
:::
