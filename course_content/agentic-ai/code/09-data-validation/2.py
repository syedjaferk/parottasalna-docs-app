from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool


# Valid data
p = Product(id=1, name="Keyboard", price=999.0, in_stock=True)
print(p)
print(p.model_dump())  # convert back to a dict
print(p.model_dump_json())  # convert to a JSON string



# try:
#     Product(id="abc", name="Keyboard", price=999.0, in_stock=True)
# except ValidationError as e:
#     print(e.errors())