import sys
from parser import Loader


def main() -> None:
    if (len(sys.argv) != 2):
        print("Usage: python3 . <maps/map_file>")
        sys.exit(1)

    map_file = sys.argv[1]
    loader = Loader()
    try:
        parameters = loader.load_file(map_file)
    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m {e}\n")
        sys.exit(1)
    print(f"{parameters}")

if __name__ == "__main__":
    main()
