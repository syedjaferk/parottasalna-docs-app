import time


def make_tea():
    print("Boiling water...")
    time.sleep(3)
    print("Tea is ready!")


def make_toast():
    print("Toasting bread...")
    time.sleep(3)
    print("Toast is ready!")


def main():
    make_toast()
    make_tea()


main()
