# Chapter 19 · Design Unified Payments Interface (UPI)

## The problem

Let a person pay another person or shop, from any bank account to any other, in seconds, using a
phone. UPI is a real-time payment system with many apps (PSPs), many banks and one central switch
(NPCI). Money must **never be lost, never be debited twice, never be created**.

```{raw} html
:file: ../diagrams/upi.html
```

## Actors

- **Payer / payee apps** (PhonePe, Google Pay, a bank app), each backed by a PSP bank.
- **UPI switch** (run by NPCI): routes requests, keeps a record, resolves a virtual payment address
  (VPA) such as `name@bank` to the right bank.
- **Issuer (payer) bank** debits. **Beneficiary (payee) bank** credits.

## Requirements

- Pay by VPA, QR or phone number; collect requests; check balance; payment status.
- **Exactly-once effect**: a retry must not charge twice.
- Fast: a payment should finish in a few seconds.
- Very high availability and **auditable**: every rupee traceable.
- Scale: billions of transactions a month, about **5,000-10,000 per second** at peak.

## A payment in steps

1. Payer enters the amount and **PIN** (the PIN is encrypted on the phone and only the payer's bank can read it).
2. The app creates a payment request with a unique **transaction id** and sends it to its PSP, then to
   the switch.
3. The switch looks up the payee VPA, and asks the **payer bank to debit**.
4. On success it asks the **payee bank to credit**.
5. The switch records the final status and notifies both apps (push / SMS).

## Hard problems and answers

- **Idempotency:** the transaction id is the idempotency key. The same request twice returns the
  stored result.
- **Atomicity across two banks:** you cannot do one database transaction across banks. Use a
  **saga**: debit, then credit; if credit fails, run a **reversal** (credit back the payer).
- **Unknown state (timeout):** after a timeout the switch does not guess. It runs **status
  enquiry / reconciliation** against the banks until the outcome is certain.
- **Double entry ledger:** each transfer writes two entries that sum to zero. Append-only, never edited.
- **Ordering and hot accounts:** shard ledgers by account id; serialise updates per account.
- **Fraud and limits:** per-day amount limits, velocity checks, device binding, risk score before debit.
- **Availability:** active-active data centres, queues for notifications, graceful degradation when a
  bank is slow (show "pending", not "failed").

## Consistency choice

Money needs **strong consistency** inside each bank's ledger. Between systems you accept
**eventual consistency with reconciliation**, and make every step visible in an audit trail.

## Common mistakes

- Assuming a distributed transaction across banks exists.
- Treating a timeout as a failure and retrying the debit.
- Updating a balance without a ledger entry.
- Forgetting reconciliation and reversals.

:::{admonition} Try it in the playground
:class: important
Build it in [Design UPI](/system-design/upi/).
:::
