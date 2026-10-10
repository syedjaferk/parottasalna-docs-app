from fastapi import FastAPI

app = FastAPI()

@app.get("/orders/user/{user_id}")
def get_orders(user_id: int):
    return {
        "orders": [
            {
                "id": 101,
                "amount": 500
            },
            {
                "id": 102,
                "amount": 900
            }
        ]
    }
