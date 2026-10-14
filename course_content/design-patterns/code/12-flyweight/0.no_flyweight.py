"""Without Flyweight: every tree carries its own copy of the heavy texture."""
import sys


class Tree:
    def __init__(self, x, y, species, texture):
        self.x, self.y = x, y
        self.species = species
        self.texture = texture          # imagine 1 MB of image data


# "x" * 1_000_000 builds a new 1 MB string for every tree
forest = [Tree(i, i, "Neem", "x" * 1_000_000) for i in range(100)]
total = sum(sys.getsizeof(t.texture) for t in forest)
print(f"{total / 1e6:.0f} MB just for textures")
