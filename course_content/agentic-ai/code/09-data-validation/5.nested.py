from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    pincode: str


class Customer(BaseModel):
    name: str
    email: str
    address: Address  # nested model


class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: float


class Order(BaseModel):
    order_id: int
    customer: Customer
    items: list[OrderItem]  # list of nested models
    total_amount: float


order_data = {
    "order_id": 101,
    "customer": {
        "name": "Ravi",
        "email": "ravi@example.com",
        "address": {"street": "MG Road", "city": "Coimbatore", "pincode": "641001"},
    },
    "items": [
        {"product_name": "Mouse", "quantity": 2, "price": 500.0},
        {"product_name": "Mousepad", "quantity": 1, "price": 200.0},
    ],
    "total_amount": 1200.0,
}

order = Order(**order_data)
print(order.customer.address.city)  # Coimbatore
