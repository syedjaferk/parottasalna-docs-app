# data_structures.py - lists and dictionaries
# A LIST keeps things in order. Positions start at 0.
fruits = ["apple", "banana", "mango"]
print(fruits[0])             # apple
print(fruits[-1])            # mango  (-1 means "the last one")
fruits.append("grape")       # add to the end
print(len(fruits))           # 4
for fruit in fruits:
    print("I like", fruit)

# A DICTIONARY stores pairs: a label (key) and a value.
person = {"name": "Asha", "age": 21, "city": "Chennai"}
print(person["name"])        # Asha
person["age"] = 22           # change a value
person["email"] = "asha@example.com"   # add a new pair
print(person.get("phone", "not given"))  # safe lookup with a default

# Lists and dictionaries nest. THIS is exactly how a chat with an AI is stored:
messages = [
    {"role": "system", "content": "You are a friendly assistant."},
    {"role": "user", "content": "Hi! What is Python?"},
]
messages.append({"role": "assistant", "content": "Python is a programming language."})
for m in messages:
    print(f"{m['role']:>9}: {m['content']}")
