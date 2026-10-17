# Chapter 14 · Design a parking garage (object-oriented design)

## The problem

This one is a **low-level design** question: instead of servers, you design **classes**. Park and
unpark vehicles, find a free spot of the right size, compute the fee.

```{raw} html
:file: ../diagrams/parking-garage.html
```

## Requirements to ask for

- Vehicle types (motorcycle, car, truck) and spot sizes (small, medium, large).
- Several floors, several entrances/exits.
- Pay at an exit kiosk; pricing per hour, maybe different per vehicle type.
- Show "garage full" or free-spot counts.

## The classes

| Class | Responsibility |
|---|---|
| `ParkingLot` | Entry point: `park(vehicle) -> Ticket`, `unpark(ticket) -> Receipt` |
| `Floor` | Knows its spots, finds a free spot of a given size |
| `Spot` | Size, whether free, `can_fit(vehicle)`, `assign`, `release` |
| `Vehicle` | Base class; `Motorcycle`, `Car`, `Truck` set the size they need |
| `Ticket` | Id, vehicle, spot, entry time |
| `PricingPolicy` | `fee(ticket, exit_time)`; `HourlyPolicy`, `FlatPolicy` |
| `Payment` | Records the charge; success or failure |

```python
class Spot:
    def __init__(self, spot_id, size):
        self.id, self.size, self.vehicle = spot_id, size, None
    def can_fit(self, vehicle):
        return self.vehicle is None and self.size >= vehicle.required_size
    def assign(self, vehicle): self.vehicle = vehicle
    def release(self): self.vehicle = None

class ParkingLot:
    def park(self, vehicle):
        for floor in self.floors:
            spot = floor.find_spot(vehicle)       # smallest free spot that fits
            if spot:
                spot.assign(vehicle)
                return Ticket(vehicle, spot, now())
        raise GarageFull()
```

## Design patterns worth naming

- **Strategy** for pricing (swap `HourlyPolicy` for `FlatPolicy` without touching `ParkingLot`).
- **Factory** to create a `Vehicle` from input.
- **Singleton** (carefully) for the lot object, or just pass it in.
- Keep **open/closed**: adding "electric vehicle spot" should add code, not change old code.

## Concurrency and scale

Two cars at two entrances can grab the same spot. Make `assign` **atomic** (a lock per floor, or a
database row update with a condition "only if free"). For a chain of garages, keep spot status in a
database and cache the free count per floor.

## Common mistakes

- One giant `ParkingLot` class doing everything.
- Hard-coding the fee rules inside the ticket.
- Ignoring that two threads can pick the same spot.

:::{admonition} Try it in the playground
:class: important
Design the classes in [Design a Parking Garage](/system-design/parking-garage/).
:::
