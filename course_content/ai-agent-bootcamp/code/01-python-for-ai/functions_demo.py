# functions_demo.py - functions are the building blocks of agents
def add(a, b):
    """Add two numbers and give back the answer."""
    return a + b


def greet(name, shout=False):
    """Make a greeting. 'shout' is optional; it defaults to False."""
    message = f"Hello, {name}!"
    if shout:
        message = message.upper()
    return message


print(add(2, 3))                 # 5
print(greet("Asha"))             # Hello, Asha!
print(greet("Asha", shout=True)) # HELLO, ASHA!

# A function can also use other functions:
def total_price(prices):
    total = 0
    for p in prices:             # repeat for each item in the list
        total = add(total, p)
    return total


print(total_price([10, 20, 5]))  # 35
