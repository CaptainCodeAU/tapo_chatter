"""Main module for tapo."""

from tapo import hello

def main() -> None:
    """Run the main application logic."""
    message = hello()
    print(message)

if __name__ == "__main__":
    main()
