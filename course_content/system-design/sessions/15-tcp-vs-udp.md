# Chapter 15 · TCP vs UDP

## The big idea

Both move data between two programs over IP. They make opposite promises:

- **TCP** promises **every byte arrives, once, in order**, or you will be told it failed.
- **UDP** promises **nothing**: it sends the packet and forgets it.

**Everyday example:** TCP is **registered post with signature**: slower, you know it arrived, lost
letters are resent. UDP is **shouting across a field**: instant, but if the wind carries your words away,
nobody repeats them.

```{raw} html
:file: ../diagrams/tcp-vs-udp.html
```

## TCP in detail

**1. Handshake (connection setup).** Before any data, client and server agree:

```text
client -> server : SYN         "I want to talk, my sequence starts at 1000"
server -> client : SYN-ACK     "OK, mine starts at 5000, I got your 1000"
client -> server : ACK         "Got it"                 (now data may flow)
```

That costs **one round trip** (about 0.5 ms inside a data centre, 100+ ms across an ocean).

**2. Sequence numbers and acknowledgements.** Every segment is numbered. The receiver acknowledges.
If an acknowledgement does not arrive in time, the sender **retransmits**.

**3. Flow control.** The receiver advertises how much buffer it has (the **window**), so a fast sender
cannot drown a slow receiver.

**4. Congestion control.** On packet loss TCP slows down (**slow start**, **AIMD**) so the network is
shared fairly. This is why one TCP connection takes a moment to reach full speed.

**5. Teardown.** `FIN` / `ACK` both ways.

## UDP in detail

One datagram = one packet with a tiny 8-byte header (ports, length, checksum). No handshake, no
retransmission, no ordering, no congestion control. The application receives datagrams as they arrive,
possibly out of order, possibly duplicated, possibly not at all.

## Watching TCP repair loss and UDP not

```python
import random
random.seed(4)

def lossy_channel(packet, loss=0.3):
    """Delivers the packet with 70% probability."""
    return packet if random.random() > loss else None

# UDP style: send each message once
udp_received = [m for m in range(10) if lossy_channel(m) is not None]
print("UDP sent 10, received", len(udp_received), "->", udp_received)

# TCP style: resend until acknowledged
sends = 0
tcp_received = []
for m in range(10):
    while True:
        sends += 1
        if lossy_channel(m) is not None:      # it arrived: the ACK comes back, stop resending
            tcp_received.append(m)
            break
print("TCP sent 10, received", len(tcp_received), "in order, after", sends, "transmissions")
```

**Output:**

```text
UDP sent 10, received 5 -> [2, 5, 6, 7, 8]
TCP sent 10, received 10 in order, after 15 transmissions
```

TCP delivered everything but needed extra transmissions (and extra waiting). UDP lost messages but
never waited.

## Head-of-line blocking

TCP delivers bytes **in order**. If packet 3 is lost, packets 4, 5, 6 wait in a buffer until 3 is
retransmitted, even though they have arrived. For a web page that is fine; for live video it is a
disaster, and **HTTP/2 over TCP** suffers from it across all multiplexed streams. **HTTP/3 and QUIC**
run over UDP and handle loss per stream.

## Side by side

| | TCP | UDP |
|---|---|---|
| Connection | Handshake first | None |
| Delivery | Guaranteed, ordered, no duplicates | Best effort |
| Header | 20+ bytes | 8 bytes |
| Speed | Slower start, congestion-controlled | Fast, no backing off |
| Good for | Web, APIs, databases, email, file transfer, SSH | Voice/video calls, games, DNS, DHCP, streaming metrics, **QUIC/HTTP/3** |
| Broadcast / multicast | No | Yes |

## Choosing in an interview

- Needs **correctness**: payments, orders, files, database traffic: **TCP**.
- **Fresh beats perfect**: a video frame that arrives late is useless: **UDP**.
- **Many tiny request/response pairs** (DNS lookups): **UDP** (one packet each way, no setup).
- Want reliability **and** low latency (new protocol): **QUIC** (UDP with reliability built in).

## Real sockets, both kinds

```python
import socket, threading

def tcp_echo(server):
    conn, _ = server.accept()
    with conn:
        conn.sendall(conn.recv(1024).upper())

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(("127.0.0.1", 0)); tcp.listen(1)
threading.Thread(target=tcp_echo, args=(tcp,), daemon=True).start()

client = socket.create_connection(tcp.getsockname())          # handshake happens here
client.sendall(b"hello over tcp")
print("TCP reply:", client.recv(1024))
client.close()

udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind(("127.0.0.1", 0))
udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_client.sendto(b"hello over udp", udp_server.getsockname())   # no connection, no handshake
data, _ = udp_server.recvfrom(1024)
print("UDP got  :", data)
```

**Output:**

```text
TCP reply: b'HELLO OVER TCP'
UDP got  : b'hello over udp'
```

The TCP side needed `listen`, `accept` and `create_connection` (the handshake). The UDP side just
sent a datagram.

## Design consequences

- **Each new TCP connection costs a round trip (plus TLS).** Reuse connections with keep-alive and
  connection pools. Opening a database connection per request is a classic mistake.
- Set **timeouts** on every socket; an unresponsive peer can hold a TCP connection for minutes.
- On UDP you must handle **loss, duplication and ordering yourself** if you care.

## Common mistakes

:::{warning}
- Choosing UDP because "it is faster" and then rebuilding a worse TCP.
- Opening a new TCP connection for every request.
- No timeouts, so dead peers hang threads.
- Assuming UDP is unusable on the internet: DNS, QUIC and video calls depend on it.
:::

## Try it yourself

1. Why do online games use UDP but a banking app uses TCP?
2. A page makes 8 sequential HTTPS calls over a 80 ms round trip using a **new** connection each time (TCP + TLS 1.3 needs 2 round trips of setup). How much time is spent just on setup? How does keep-alive help?
3. What is head-of-line blocking and which protocol fixes it for HTTP?

<details class="solution"><summary>Answers</summary>

1. A game wants the *latest* position; an old one is worthless, so retransmitting is wasteful. A bank transfer must arrive completely and in order.
2. 8 x 2 x 80 = **1,280 ms** of setup. Keep-alive reuses one connection, so setup is paid once (160 ms).
3. One lost packet stalls everything behind it in a TCP stream. **HTTP/3 (QUIC over UDP)** makes streams independent.

</details>

:::{admonition} Next
:class: important
Bits get flipped in transit. How do we notice? [Checksums](16-checksums.md).
:::
