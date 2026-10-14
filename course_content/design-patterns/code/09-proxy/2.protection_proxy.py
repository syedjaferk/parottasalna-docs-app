"""A protection proxy: same interface, but it checks permission first."""


class Database:
    def delete(self, table): print(f"deleted {table}")
    def read(self, table): print(f"read {table}")


class SecureDatabase:
    def __init__(self, db, user):
        self._db, self._user = db, user

    def read(self, table):
        self._db.read(table)                     # everyone may read

    def delete(self, table):
        if self._user["role"] != "admin":
            raise PermissionError("only admins can delete")
        self._db.delete(table)


viewer = SecureDatabase(Database(), {"name": "Kavya", "role": "viewer"})
admin = SecureDatabase(Database(), {"name": "Arun", "role": "admin"})

viewer.read("users")
admin.delete("old_logs")
try:
    viewer.delete("users")
except PermissionError as e:
    print("PermissionError:", e)
