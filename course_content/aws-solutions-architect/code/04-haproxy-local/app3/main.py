from fastapi import FastAPI
import socket

app = FastAPI()

@app.get("/")
def home():
    return {
        "server": "app3",
        "hostname": socket.gethostname()
    }

@app.get("/health")
def health():
    return {"status": "UP"}
