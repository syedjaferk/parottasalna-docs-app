import requests
import time

url = "http://localhost:8081"

for itr in range(1000):
    req = requests.get(url)
    print(req.json())
    time.sleep(0.5)
