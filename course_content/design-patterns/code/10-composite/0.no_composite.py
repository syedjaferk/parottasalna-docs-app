"""Without Composite: every function checks "is it a file or a folder?"."""

tree = {"name": "project", "children": [
    {"name": "main.py", "size": 4},
    {"name": "docs", "children": [{"name": "readme.md", "size": 1}]},
]}


def total_size(item):
    if "children" in item:                      # folder
        return sum(total_size(child) for child in item["children"])
    return item["size"]                         # file


print(total_size(tree))    # 5
