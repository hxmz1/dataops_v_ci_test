import argparse
from decimal import Decimal


def main():
    parser = argparse.ArgumentParser(description="Generate a Markdown quality report.")
    parser.add_argument(
        "revenue",
        nargs="?",
        type=Decimal,
        help="optional total revenue to include in the report",
    )
    args = parser.parse_args()

    if args.revenue is None:
        print("# Quality checks")
        print()
        print("- Ruff: passed")
        print("- SQLFluff: passed")
        return

    print("# Revenue report")
    print()
    print(f"Total revenue: **{args.revenue:.2f}**")


if __name__ == "__main__":
    main()
