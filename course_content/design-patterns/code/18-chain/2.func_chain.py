"""A simple function-based chain: a list of checks run in order."""


def has_token(req):   return None if req.get("token") else "401 not logged in"
def not_blocked(req): return "403 blocked" if req["user"] == "spammer" else None


checks = [has_token, not_blocked]


def run(req):
    for check in checks:
        error = check(req)
        if error:
            return error
    return "200 ok"


print(run({"token": "abc", "user": "kavya"}))     # 200 ok
print(run({"token": "", "user": "kavya"}))        # 401 not logged in
print(run({"token": "abc", "user": "spammer"}))   # 403 blocked
