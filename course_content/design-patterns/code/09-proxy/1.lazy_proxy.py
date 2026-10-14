"""A virtual (lazy) proxy: create the expensive object only when it is first used."""


class RealImage:
    def __init__(self, path):
        print(f"Loading {path} from disk... (slow)")
        self.path = path

    def show(self):
        print(f"Showing {self.path}")


class LazyImage:
    def __init__(self, path):
        self.path = path
        self._real = None

    def show(self):
        if self._real is None:
            self._real = RealImage(self.path)      # created on first use
        self._real.show()


gallery = [LazyImage(f"photo{i}.jpg") for i in range(5)]    # instant
gallery[0].show()    # loads only photo0
gallery[0].show()    # already loaded
