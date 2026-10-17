# Chapter 80 · Design UPI (Unified Payments Interface)

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [Idempotency](27-idempotency.md)
- [ACID transactions](29-acid.md)
- [Microservices (sagas)](56-microservices.md)
- [Message queues](44-message-queues.md)
- [Strong vs eventual consistency](66-strong-vs-eventual-consistency.md)
- [Circuit breaker](52-circuit-breaker.md)
- [Disaster recovery](53-disaster-recovery.md)
- [Distributed tracing](54-distributed-tracing.md)

## The problem

Let a person pay another person or a shop, from **any bank account to any other**, in seconds, using a phone and a
virtual address or QR code. UPI is a real-time payment system with many apps, many banks and one central **switch**.
The rules are strict: money must **never be lost, debited twice or created**, and every rupee must be traceable.

```{raw} html
:file: ../diagrams/upi.html
```

## Step 1: actors and requirements

| Actor | Role |
|---|---|
| **Payer / payee app** (PhonePe, Google Pay, a bank app) | The user interface |
| **PSP** (payment service provider) | The bank behind an app; connects it to the switch |
| **Switch** (run by NPCI) | Routes requests, resolves addresses, records every transaction |
| **Payer bank (issuer)** | Holds the payer's money and **debits** it |
| **Payee bank (beneficiary)** | **Credits** the payee's account |

**Functional:** pay by virtual payment address (VPA, `name@bank`), QR or phone number; request money ("collect");
check status; check balance; **reverse** a failed payment.

**Non-functional:** correct above all (exactly-once effect); finishes in a few seconds; very high availability;
secure (the PIN is encrypted on the device and only the issuing bank can read it); fully **auditable**.

**Out of scope:** the mobile app, regulatory process, merchant onboarding.

## Step 2: estimate

```python
txns_per_month = 15_000_000_000
peak_factor = 3
entries_per_txn, bytes_per_entry = 2, 200            # a debit entry and a credit entry

per_day = txns_per_month / 30
avg_tps = per_day / 86_400
peak_tps = avg_tps * peak_factor
ledger_gb_per_day = per_day * entries_per_txn * bytes_per_entry / 1e9
ledger_tb_per_year = ledger_gb_per_day * 365 / 1000

downtime_min_per_year = 365 * 24 * 60 * (1 - 0.9999)

print(f"transactions per day : {per_day / 1e6:,.0f} million")
print(f"throughput           : {avg_tps:,.0f} per second average, {peak_tps:,.0f} at peak")
print(f"ledger growth        : {ledger_gb_per_day:,.0f} GB per day, about {ledger_tb_per_year:,.0f} TB per year")
print(f"99.99% availability  : at most {downtime_min_per_year:.0f} minutes of downtime a year")
```

**Output:**

```text
transactions per day : 500 million
throughput           : 5,787 per second average, 17,361 at peak
ledger growth        : 200 GB per day, about 73 TB per year
99.99% availability  : at most 53 minutes of downtime a year
```

About **17,000 transactions per second at peak**, each touching several systems, and almost no allowed downtime.
Every shared component must scale horizontally.

## Step 3: the happy path

```text
1. Payer enters the amount and PIN. The PIN is encrypted on the phone; only the payer's bank can read it.
2. The app creates a payment request with a UNIQUE TRANSACTION ID and sends it to its PSP, which forwards it to the switch.
3. The switch resolves the payee's VPA to a bank (the VPA directory).
4. The switch asks the PAYER bank to DEBIT.   -> if that fails, stop: nothing moved.
5. The switch asks the PAYEE bank to CREDIT.
6. The switch records the final status, and both apps are notified.
```

Debit **first**, then credit: never credit money that has not left. There is no single database spanning two banks,
so this is a **saga** (a sequence of local steps with a way to undo them).

## Step 4: idempotency, the rule that prevents double charges

The client creates the **transaction id before the first attempt** and reuses it on every retry. Each bank stores the
result under that id and, if it sees the id again, **returns the stored result without moving money again**.

## Step 5: the working model, a ledger, a saga and honest uncertainty

```python
class Bank:
    def __init__(self, name, balances):
        self.name, self.balances = name, dict(balances)
        self.ledger = []                          # append-only entries: (txn_id, account, amount)
        self.results = {}                         # idempotency: txn_id -> result

    def debit(self, txn_id, account, amount):
        if txn_id in self.results:
            return self.results[txn_id]           # a retry: return the stored result, move nothing
        if self.balances[account] < amount:
            result = "INSUFFICIENT_FUNDS"
        else:
            self.balances[account] -= amount
            self.ledger.append((txn_id, account, -amount))
            result = "DEBITED"
        self.results[txn_id] = result
        return result

    def credit(self, txn_id, account, amount, fail=None):
        if txn_id in self.results:
            return self.results[txn_id]
        if account not in self.balances:
            self.results[txn_id] = "ACCOUNT_CLOSED"
            return "ACCOUNT_CLOSED"
        self.balances[account] += amount
        self.ledger.append((txn_id, account, +amount))
        self.results[txn_id] = "CREDITED"
        if fail == "lose_reply":                  # the credit HAPPENED, but the answer never reaches the switch
            raise TimeoutError("no reply from the payee bank")
        return "CREDITED"

    def status(self, txn_id):
        return self.results.get(txn_id, "UNKNOWN")

class Switch:
    def __init__(self):
        self.status = {}

    def pay(self, txn_id, payer_bank, payer, payee_bank, payee, amount, credit_fault=None):
        if txn_id in self.status and self.status[txn_id] != "PENDING":
            return self.status[txn_id]                                   # idempotent: same id, same outcome
        if payer_bank.debit(txn_id + ":d", payer, amount) != "DEBITED":
            self.status[txn_id] = "FAILED (nothing moved)"
            return self.status[txn_id]
        try:
            result = payee_bank.credit(txn_id + ":c", payee, amount, fail=credit_fault)
        except TimeoutError:
            self.status[txn_id] = "PENDING"                                 # a timeout means UNKNOWN, not failure
            return "PENDING (waiting for the bank to confirm)"
        if result == "CREDITED":
            self.status[txn_id] = "SUCCESS"
        else:
            payer_bank.balances[payer] += amount                            # compensation: reverse the debit
            payer_bank.ledger.append((txn_id + ":r", payer, +amount))
            self.status[txn_id] = "REVERSED (credit failed, money returned)"
        return self.status[txn_id]

    def reconcile(self, txn_id, payee_bank):
        """Ask the bank what really happened and settle the pending payment."""
        if payee_bank.status(txn_id + ":c") == "CREDITED":
            self.status[txn_id] = "SUCCESS"
        return self.status[txn_id]

def total(*banks):
    return sum(sum(b.balances.values()) for b in banks)

bank_a = Bank("A", {"asha": 1000})
bank_b = Bank("B", {"ravi": 200})
switch = Switch()
start_total = total(bank_a, bank_b)

print("1. normal payment          :", switch.pay("T1", bank_a, "asha", bank_b, "ravi", 300))
print("2. retry of T1 (user taps twice):", switch.pay("T1", bank_a, "asha", bank_b, "ravi", 300))
print("   balances                :", bank_a.balances, bank_b.balances)
print("3. insufficient funds      :", switch.pay("T2", bank_a, "asha", bank_b, "ravi", 5000))
print("4. payee account closed    :", switch.pay("T3", bank_a, "asha", bank_b, "nobody", 100))
print("   asha after the reversal :", bank_a.balances["asha"])
print("5. credit done, reply lost :", switch.pay("T4", bank_a, "asha", bank_b, "ravi", 50, credit_fault="lose_reply"))
print("   status right now        :", switch.status["T4"])
print("   after reconciliation    :", switch.reconcile("T4", bank_b))
print()
print("money in the system before :", start_total)
print("money in the system after  :", total(bank_a, bank_b), "(never created or destroyed)")
```

**Output:**

```text
1. normal payment          : SUCCESS
2. retry of T1 (user taps twice): SUCCESS
   balances                : {'asha': 700} {'ravi': 500}
3. insufficient funds      : FAILED (nothing moved)
4. payee account closed    : REVERSED (credit failed, money returned)
   asha after the reversal : 700
5. credit done, reply lost : PENDING (waiting for the bank to confirm)
   status right now        : PENDING
   after reconciliation    : SUCCESS

money in the system before : 1200
money in the system after  : 1200 (never created or destroyed)
```

Walk through what each case teaches:

- **1 and 2:** the retry with the same transaction id **did not debit again**: idempotency.
- **3:** insufficient funds fails at the debit step, so nothing moved.
- **4:** the debit succeeded but the credit failed, so the switch **ran a compensating reversal**: the saga undoing a
  step.
- **5:** the credit actually happened but the reply was lost. The switch did **not** assume failure (reversing would have
  created money); it marked the payment **PENDING**, then **asked the bank** (reconciliation) and learned the truth.
- Total money in the system never changed.

## Step 6: a double-entry ledger you can audit

Every transfer writes **two entries that sum to zero**. Balances are the sum of entries. Nothing is ever edited; a
mistake is fixed by a new, reversing entry.

```python
# continues from the previous example (bank_a, bank_b and the switch)
ledger = bank_a.ledger + bank_b.ledger
print("entries:", len(ledger))
by_txn = {}
for txn_id, account, amount in ledger:
    by_txn.setdefault(txn_id.split(":")[0], []).append(amount)
for txn, amounts in sorted(by_txn.items()):
    print(f"  {txn}: entries {amounts} sum = {sum(amounts)}")
print("every completed transfer sums to zero; the reversal (T3) nets out as well")
```

**Output:**

```text
entries: 6
  T1: entries [-300, 300] sum = 0
  T3: entries [-100, 100] sum = 0
  T4: entries [-50, 50] sum = 0
every completed transfer sums to zero; the reversal (T3) nets out as well
```

## Step 7: the remaining hard problems

| Problem | Answer |
|---|---|
| **Timeouts** | A timeout means **unknown**: show "pending", then **status enquiry and reconciliation** with the same transaction id |
| **Ordering and hot accounts** | Shard ledgers by account id; serialise updates to one account, run different accounts in parallel |
| **Fraud** | Device binding, per-day and per-transaction limits, real-time risk scoring (velocity, new payee, odd hours) before the debit |
| **Availability** | Active-active sites, queues for notifications, per-bank circuit breakers and a graceful "bank is slow, payment pending" mode |
| **Auditability** | Append-only ledger, immutable logs, daily bank-to-switch reconciliation files |
| **Disaster recovery** | Synchronous replication inside a site and across sites for the ledger (RPO about zero) |

**Consistency model:** **strong consistency inside each bank's ledger** (ACID, because balances must be exact) and
**eventual consistency with reconciliation between systems**, with every step visible in an audit trail.

## Trade-offs

| Choice | You gain | You pay |
|---|---|---|
| Saga with reversals | Works across independent banks | Temporary "pending" states |
| Append-only ledger | A full audit trail, simple reconciliation | More storage; balances are derived |
| Queues for non-critical work | A short critical path | Notifications are slightly delayed |
| Synchronous cross-site replication | Zero data loss | Higher write latency |

## Common mistakes

:::{warning}
- Assuming a distributed transaction across banks exists.
- Treating a timeout as a failure and retrying the debit with a new id.
- Updating a balance without writing a ledger entry.
- Forgetting reconciliation and reversal flows.
- Generating the transaction id on the server (a lost reply leaves the client unable to retry safely).
:::

## Try it yourself

1. In the model, what would go wrong if the switch treated the timeout in case 5 as a failure and reversed the debit?
2. Why is the transaction id created by the client, before the first attempt?
3. Which consistency does each bank's ledger need, and which holds between banks?

<details class="solution"><summary>Answers</summary>

1. The credit had already happened, so Ravi would keep the money **and** Asha would be refunded: money would be **created** (the totals would no longer match).
2. If the server created it, a lost response would leave the client without the id, so it could not retry the same operation safely. A client-generated id makes retries recognisable.
3. Strong consistency (ACID) inside each bank; eventual consistency with reconciliation between systems.

</details>

:::{admonition} Try it in the playground
:class: important
Build it in [Design UPI](/system-design/upi/).
:::

:::{admonition} Next
:class: important
That completes the course. Re-do each design in the [System Design playground](/system-design/) without notes, and explain every box out loud.
:::
