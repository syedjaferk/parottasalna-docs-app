# Chapter 75 · Design a parking garage (object-oriented design)

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [API design](24-api-design.md)
- [ACID transactions](29-acid.md)
- [Concurrency vs parallelism](62-concurrency-vs-parallelism.md)
- [Database indexes](31-database-indexes.md)

## The problem

This is a **low-level (object-oriented) design** question. There are no servers to size; you design **classes**:
park and unpark vehicles, find a free spot that fits, and compute the fee. The interviewer is looking at your class
responsibilities, your use of patterns, and whether you notice **two cars choosing the same spot**.

```{raw} html
:file: ../diagrams/parking-garage.html
```

## Step 1: clarify requirements

Ask, then write the answers down:

- Vehicle types? **Motorcycle, car, truck.** Spot sizes? **Small, medium, large.** A bigger spot may hold a smaller vehicle.
- Several floors and several entrances? **Yes.**
- Pricing? **First hour 40, then 30 for each extra started hour.**
- Pay at exit? **Yes.** Show "garage full" and free-spot counts? **Yes.**
- Out of scope: reservations, EV charging, licence-plate recognition, hardware barriers.

## Step 2: find the classes (nouns become classes, verbs become methods)

| Class | Responsibility |
|---|---|
| `Vehicle` (`Motorcycle`, `Car`, `Truck`) | Knows what **size of spot** it needs |
| `Spot` | Has a size; knows whether it is free and whether a vehicle **fits** |
| `Floor` | Owns its spots; **finds and reserves** the best free spot |
| `Ticket` | Links a vehicle to a spot and an entry time |
| `PricingPolicy` | Computes the **fee** for a stay (a replaceable strategy) |
| `ParkingLot` | The entry point: `park(vehicle)` and `unpark(ticket)` |

Design principles in play: **single responsibility** (each class has one job), **polymorphism** (vehicles ask for
their own size, so there is no `if vehicle_type == "car"` chain), and the **Strategy pattern** (swap the pricing rule
without touching anything else).

## Step 3: the complete implementation

```python
import math
import threading
from enum import IntEnum

class Size(IntEnum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class Vehicle:
    required = Size.MEDIUM
    def __init__(self, plate):
        self.plate = plate
class Motorcycle(Vehicle): required = Size.SMALL
class Car(Vehicle):        required = Size.MEDIUM
class Truck(Vehicle):      required = Size.LARGE

class Spot:
    def __init__(self, spot_id, size):
        self.id, self.size, self.vehicle = spot_id, size, None
    def can_fit(self, vehicle):
        return self.vehicle is None and self.size >= vehicle.required

class Floor:
    def __init__(self, number, spots):
        self.number, self.spots, self._lock = number, spots, threading.Lock()
    def park(self, vehicle):
        with self._lock:                                   # the check and the assignment are one atomic step
            candidates = [s for s in self.spots if s.can_fit(vehicle)]
            if not candidates:
                return None
            spot = min(candidates, key=lambda s: s.size)   # smallest spot that fits keeps big spots free
            spot.vehicle = vehicle
            return spot
    def free_count(self):
        return sum(1 for s in self.spots if s.vehicle is None)

class Ticket:
    _next_id = 1
    def __init__(self, vehicle, spot, floor, entered_at):
        self.id, self.vehicle, self.spot, self.floor, self.entered_at = Ticket._next_id, vehicle, spot, floor, entered_at
        Ticket._next_id += 1

class HourlyPricing:
    def __init__(self, first_hour=40, extra_hour=30):
        self.first_hour, self.extra_hour = first_hour, extra_hour
    def fee(self, minutes):
        hours = max(1, math.ceil(minutes / 60))             # every started hour counts
        return self.first_hour + (hours - 1) * self.extra_hour

class GarageFull(Exception):
    pass

class ParkingLot:
    def __init__(self, floors, pricing):
        self.floors, self.pricing = floors, pricing
    def park(self, vehicle, now):
        for floor in self.floors:
            spot = floor.park(vehicle)
            if spot:
                return Ticket(vehicle, spot, floor, now)
        raise GarageFull(f"no spot for {vehicle.plate}")
    def unpark(self, ticket, now):
        fee = self.pricing.fee(now - ticket.entered_at)
        ticket.spot.vehicle = None                          # free the spot after the fee is computed
        return fee
    def free_spots(self):
        return {f.number: f.free_count() for f in self.floors}

lot = ParkingLot(
    floors=[Floor(0, [Spot("0-S1", Size.SMALL), Spot("0-M1", Size.MEDIUM), Spot("0-L1", Size.LARGE)]),
            Floor(1, [Spot("1-M1", Size.MEDIUM), Spot("1-M2", Size.MEDIUM)])],
    pricing=HourlyPricing(),
)

bike = lot.park(Motorcycle("TN01-1111"), now=0)
car = lot.park(Car("TN01-2222"), now=5)
truck = lot.park(Truck("TN01-3333"), now=10)
print("bike parked in :", bike.spot.id, "(smallest spot that fits)")
print("car parked in  :", car.spot.id)
print("truck parked in:", truck.spot.id)
print("free spots     :", lot.free_spots())

lot.park(Car("TN01-4444"), now=20)
lot.park(Car("TN01-5555"), now=25)
try:
    lot.park(Car("TN01-6666"), now=30)
except GarageFull as full:
    print("garage full    :", full)

print("car stayed 3h10m, fee =", lot.unpark(car, now=5 + 190))
print("bike stayed 25 min, fee =", lot.unpark(bike, now=25))
print("free spots after exits:", lot.free_spots())
```

**Output:**

```text
bike parked in : 0-S1 (smallest spot that fits)
car parked in  : 0-M1
truck parked in: 0-L1
free spots     : {0: 0, 1: 2}
garage full    : no spot for TN01-6666
car stayed 3h10m, fee = 130
bike stayed 25 min, fee = 40
free spots after exits: {0: 2, 1: 0}
```

Look at what each class does *not* know: `ParkingLot` does not know how pricing works, `Spot` does not know
about money, and `Vehicle` types are just three lines each. Adding an `ElectricCar` or a `FlatRate` policy is a new
class, with no edits to the old ones (**open/closed principle**).

## Step 4: the race condition

Two cars at two entrances see the **same last spot as free** and both take it. The fix is in `Floor.park`: the
"find a free spot" check and the "assign it" step happen **inside one lock**, so only one caller can win.

```python
import threading

class Spot:
    def __init__(self):
        self.vehicle = None

spot = Spot()
lock = threading.Lock()
winners = []

def try_park(name, use_lock):
    if use_lock:
        with lock:
            if spot.vehicle is None:
                spot.vehicle = name
                winners.append(name)
    else:
        if spot.vehicle is None:               # check ...
            threading.Event().wait(0.001)      # (another car arrives right here)
            spot.vehicle = name                # ... then act
            winners.append(name)

for use_lock in (False, True):
    spot.vehicle, winners[:] = None, []
    threads = [threading.Thread(target=try_park, args=(f"car{i}", use_lock)) for i in range(20)]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"{'with lock   ' if use_lock else 'without lock'}: {len(winners)} car(s) believe they got the only spot")
```

**Output:**

```text
without lock: 9 car(s) believe they got the only spot
with lock   : 1 car(s) believe they got the only spot
```

Without the lock several cars "won" the one spot; with it exactly one did. For a **chain of garages**, replace the
in-process lock with a **conditional database update**:
`UPDATE spots SET vehicle_id = ? WHERE id = ? AND vehicle_id IS NULL` (if zero rows change, someone else got it; try the
next spot). Hold locks only for the assignment, never for the whole stay.

## Step 5: edge cases to mention

| Case | Behaviour |
|---|---|
| **Garage full** | Reject at the entrance and show the board; do not queue cars in the street |
| **Lost ticket** | Charge the maximum daily fee after verifying the plate |
| **Payment fails** | Keep the spot occupied and let the driver retry; never free the spot before payment succeeds |
| **Oversize vehicle** | Reject with a clear message |
| **Car left in a large spot** | Prefer the smallest fitting spot; a car may use a large spot only when no smaller one is free |
| **Time zones and clocks** | Use one server clock (or UTC), not the gate hardware's clock |

## Step 6: scaling up to many garages

The object model stays the same; the **state moves into a database** and the lot becomes a service:

```text
POST /v1/garages/{id}/park     {"plate": "TN01-2222", "type": "car"}   -> 201 {"ticket_id": 88, "spot": "1-M2"}
POST /v1/tickets/{id}/pay                                                -> 200 {"fee": 160}
POST /v1/tickets/{id}/exit                                               -> 204   (frees the spot)
GET  /v1/garages/{id}/availability                                       -> {"floors": {"0": 1, "1": 2}}
```

```sql
CREATE TABLE spots   (id TEXT PRIMARY KEY, garage_id INT, floor INT, size SMALL_INT, vehicle_id BIGINT NULL);
CREATE TABLE tickets (id BIGSERIAL PRIMARY KEY, spot_id TEXT, plate TEXT, entered_at TIMESTAMP, paid_at TIMESTAMP NULL);
CREATE INDEX idx_free ON spots (garage_id, size) WHERE vehicle_id IS NULL;     -- a partial index makes "find a free spot" fast
```

Keep **free counts per floor** in a counter or cache for the display board, updated on every park and exit.

## Trade-offs

| Choice | You gain | You pay |
|---|---|---|
| Strategy pattern for pricing | Rules change with no edits to core classes | One more class and interface |
| Smallest-fit spot search | Big spots stay free for trucks | A slightly longer search |
| Per-floor lock | Entrances rarely block each other | Retry logic if a spot is taken meanwhile |
| Counters for availability | Instant display | Must be kept consistent with spot state |

## Common mistakes

:::{warning}
- One giant `ParkingLot` class that does everything.
- `if vehicle_type == ...` chains instead of polymorphism.
- Hard-coding fee rules inside `Ticket`.
- Ignoring that two threads can pick the same spot.
- Freeing the spot before the payment has succeeded.
:::

## Try it yourself

1. How would you add a "first 30 minutes free" rule without changing `ParkingLot`?
2. A van needs two adjacent car spots. Which class changes?
3. Why is the smallest-fit rule better than first-fit?

<details class="solution"><summary>Answers</summary>

1. Write a new `PricingPolicy` (for example `FreeFirst30Pricing`) and pass it to the lot. Nothing else changes.
2. `Floor.park` (or a `SpotAllocator` strategy) must find **adjacent** free spots; `Vehicle` can expose `spots_needed`.
3. First-fit can put a motorcycle in a large spot, leaving no space for a truck that arrives later.

</details>

:::{admonition} Try it in the playground
:class: important
Design the classes in [Design a Parking Garage](/system-design/parking-garage/).
:::

:::{admonition} Next
:class: important
Next case study: [Design a vending machine](76-design-vending-machine.md).
:::
