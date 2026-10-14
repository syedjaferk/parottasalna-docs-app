"""Without Proxy: every image loads immediately, even ones nobody looks at."""


class ImageViewer:
    def __init__(self, path):
        print(f"Loading {path} from disk... (slow)")
        self.path = path

    def show(self):
        print(f"Showing {self.path}")


gallery = [ImageViewer(f"photo{i}.jpg") for i in range(5)]    # loads all 5 now
gallery[0].show()
