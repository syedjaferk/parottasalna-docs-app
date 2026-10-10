from fastapi import FastAPI

app = FastAPI()

@app.get("/products/{product_id}")
def get_product(product_id: int):
    return {
        "id": product_id,
        "name": "MacBook Pro",
        "price": 2000
    }
