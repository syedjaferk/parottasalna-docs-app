from fastapi import FastAPI

app = FastAPI()

@app.get("/wallet/{user_id}")
def wallet(user_id: int):
    return {
        "balance": 2500
    }
