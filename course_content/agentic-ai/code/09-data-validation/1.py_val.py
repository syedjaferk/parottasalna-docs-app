from pydantic import BaseModel, Field


class User(BaseModel):
    name: str
    age: int = Field(gt=0)


user = User(name="Kavya", age=-9)
print(user.name)
