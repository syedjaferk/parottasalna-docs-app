"""Flyweight: share the heavy, unchanging part; pass the small, unique part in."""


class TreeType:                       # flyweight: shared, read-only
    def __init__(self, species, texture):
        self.species = species
        self.texture = texture

    def draw(self, x, y):
        print(f"Drawing {self.species} at ({x}, {y})")


class TreeFactory:
    _types: dict[str, TreeType] = {}

    @classmethod
    def get(cls, species, texture):
        if species not in cls._types:
            cls._types[species] = TreeType(species, texture)
        return cls._types[species]


class Tree:                           # context: only x and y
    def __init__(self, x, y, tree_type: TreeType):
        self.x, self.y, self.type = x, y, tree_type

    def draw(self):
        self.type.draw(self.x, self.y)


TEXTURE = "x" * 1_000_000             # one 1 MB texture
forest = [Tree(i, i * 2, TreeFactory.get("Neem", TEXTURE)) for i in range(100)]
forest[0].draw()
print(len(TreeFactory._types))                          # 1
print(forest[0].type is forest[99].type)                # True
