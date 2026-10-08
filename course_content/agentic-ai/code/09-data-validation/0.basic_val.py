def create_user(data: dict):
    if "name" not in data or not isinstance(data["name"], str):
        raise ValueError("name is required and must be a string")
    if "age" not in data or not isinstance(data["age"], int):
        raise ValueError("age is required and must be an int")
    if data["age"] < 0:
        raise ValueError("age must be positive")


user_1 = {"name": "Syed Jafer K", "age": 29}

create_user(user_1)
