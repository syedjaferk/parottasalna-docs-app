"""Without Chain of Responsibility: one big function holds every check."""

blocked_users = {"spammer"}


def handle_request(req):
    if not req.get("token"):
        return "401 not logged in"
    if req["user"] in blocked_users:
        return "403 blocked"
    if req["count"] > 100:
        return "429 too many requests"
    if len(req["body"]) > 1000:
        return "413 too large"
    return "200 ok"


print(handle_request({"token": "abc", "user": "kavya", "count": 5, "body": "hi"}))
print(handle_request({"token": "abc", "user": "spammer", "count": 5, "body": "hi"}))
