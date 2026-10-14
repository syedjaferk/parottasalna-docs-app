# Patterns at a glance

All 18 patterns on one page. Use it to revise, or when you're staring at messy code and wondering
which pattern would help.

```{raw} html
:file: diagrams/map-patterns.html
```

## Creational: how objects are made

| Pattern | In one line | Everyday example | You need it when… | Python shortcut |
|---|---|---|---|---|
| [Singleton](sessions/01-singleton-pattern.md) | exactly one instance, shared by everyone | the house's one electricity meter | copies of config, a logger or a client disagree or waste resources | a module, or `@lru_cache(maxsize=1)` |
| [Factory Method](sessions/02-factory-method-pattern.md) | one place decides which class to create | a juice shop: say "mango", get mango juice | the same `if type == ...: X()` appears in many places | a dict of name → class |
| [Abstract Factory](sessions/03-abstract-factory-pattern.md) | one factory makes a whole matching family | a furniture set where every piece matches | objects must come from the same family (local vs AWS) | a class with several `create_*` methods |
| [Builder](sessions/04-builder-pattern.md) | build a complex object step by step | ordering a custom pizza | a constructor has many optional arguments, or needs checks at the end | keyword arguments + a `dataclass` |
| [Prototype](sessions/05-prototype-pattern.md) | make new objects by copying a ready one | photocopying a filled-in form | creating from scratch is slow, and copies differ only a little | `copy.deepcopy`, `dataclasses.replace` |

## Structural: how objects fit together

| Pattern | In one line | Everyday example | You need it when… | Python shortcut |
|---|---|---|---|---|
| [Adapter](sessions/06-adapter-pattern.md) | translate one interface into another | a travel plug adapter | a library's methods don't match the ones your code expects | a thin wrapper class |
| [Decorator](sessions/07-decorator-pattern.md) | wrap something to add behaviour, same interface | gift wrap, ribbon, card | you want logging, timing, retry or caching without editing the code | `@decorator` functions |
| [Facade](sessions/08-facade-pattern.md) | one simple front door to a complex system | a hotel receptionist | callers repeat the same multi-step dance across subsystems | one class with a few methods |
| [Proxy](sessions/09-proxy-pattern.md) | a stand-in that controls access to the real thing | a cheque standing in for money | you need lazy loading, caching, permission checks or logging in front of an object | a wrapper, `__getattr__` |
| [Composite](sessions/10-composite-pattern.md) | treat one item and a group of items the same | "everyone report at 9": teacher, class or whole school | your data is a tree (folders, menus, task plans) | one class with a `children` list |
| [Bridge](sessions/11-bridge-pattern.md) | split two directions of change into two hierarchies | any remote works with any TV | subclasses multiply: `SalesPDF`, `SalesCSV`, `InventoryPDF`… | pass the second object into `__init__` |
| [Flyweight](sessions/12-flyweight-pattern.md) | share the heavy, identical part between many objects | one set of printing blocks, used thousands of times | thousands of objects repeat the same big data | a cache dict, `sys.intern`, `__slots__` |

## Behavioural: how objects work together

| Pattern | In one line | Everyday example | You need it when… | Python shortcut |
|---|---|---|---|---|
| [Strategy](sessions/13-strategy-pattern.md) | plug in one of several ways to do a job | cab, bus or metro to the airport | an `if/elif` picks between algorithms and keeps growing | pass a function |
| [Observer](sessions/14-observer-pattern.md) | notify every subscriber when something happens | subscribers of a YouTube channel | one event must trigger several reactions, without coupling | a list of callbacks |
| [Command](sessions/15-command-pattern.md) | turn an action into an object | a waiter's order slip | you need undo/redo, queues, logs or replay of actions | an object with `execute()` |
| [State](sessions/16-state-pattern.md) | each state is a class that knows what's allowed | a traffic light | many methods repeat `if status == …` ladders | a transition `dict` for simple cases |
| [Template Method](sessions/17-template-method-pattern.md) | fixed steps in a base class, blanks filled by subclasses | making tea or coffee | several jobs share the same steps in the same order | a base class method calling hooks |
| [Chain of Responsibility](sessions/18-chain-of-responsibility-pattern.md) | pass a request along handlers until one stops it | support escalation: L1, L2, manager | several checks run in order and any one may stop the request | a list of functions |

## Patterns that are easy to mix up

| These two… | …look alike, but |
|---|---|
| **Factory Method vs Abstract Factory** | Factory Method creates *one* product. Abstract Factory creates a *family* of products that must match. |
| **Factory vs Strategy** | Factory decides *which object to create*. Strategy decides *which behaviour to use*. They often work together. |
| **Adapter vs Facade** | Adapter *changes* an interface so it fits. Facade *simplifies* a big system behind a new, smaller interface. |
| **Decorator vs Proxy** | Both wrap with the same interface. Decorator *adds* a feature. Proxy *controls access* (when it's created, who may call it, where it lives). |
| **Decorator vs Chain of Responsibility** | A decorator always calls the wrapped object. A handler in a chain may *stop* the request. |
| **Strategy vs State** | With Strategy, the *caller* picks the behaviour. With State, the object *changes its own* behaviour as its state changes. |
| **Strategy vs Template Method** | Strategy swaps a whole algorithm by *composition*. Template Method fixes the steps and lets *subclasses* fill gaps (inheritance). |
| **Bridge vs Strategy** | Similar code. Strategy swaps one algorithm. Bridge splits a whole class into two hierarchies that grow separately. |
| **Composite vs Decorator** | Composite has *many* children and combines their answers. A decorator wraps exactly *one* object. |
| **Flyweight vs Singleton** | Singleton has exactly one instance of a class. Flyweight has one shared instance *per kind* (one per tree species). |

## Test yourself

The **"Which pattern fits?"** quiz on this page gives you real situations and asks which pattern
solves them. It mixes all three families, so take it after you've finished the course.
