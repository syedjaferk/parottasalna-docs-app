# json_demo.py - JSON is just text that looks like a dictionary
import json

# 1. Python dictionary  ->  JSON text   (json.dumps = "dump to string")
person = {"name": "Asha", "age": 21, "skills": ["python", "sql"], "student": True}
text = json.dumps(person, indent=2)
print(text)
print(type(text))                      # <class 'str'>  - it is only text!

# 2. JSON text  ->  Python dictionary   (json.loads = "load from string")
incoming = '{"city": "Chennai", "temp": 31.5, "rain": false}'
data = json.loads(incoming)
print(data["city"], data["temp"])      # Chennai 31.5
print(type(data))                      # <class 'dict'>

# 3. Save to a file and read it back
with open("person.json", "w", encoding="utf-8") as f:
    json.dump(person, f, indent=2)

with open("person.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
print(loaded == person)                # True
