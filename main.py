from configuration import Configuration
from library import Library


def main():
    config = Configuration()
    lib = Library(config)
    lib.download_found_episode()


if __name__ == '__main__': main()