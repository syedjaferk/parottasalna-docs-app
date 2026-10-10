import requests


def collect_todo_data():
    url = "https://jsonplaceholder.typicode.com/todos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}


data = collect_todo_data()
print(len(data))
print(data[0])
