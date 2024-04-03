import argparse
from typing import Optional

def main(identifier: Optional[str]) -> None:
    print("Started")
    running = True
    while running:
        cmd = input("")
        print(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--identifier",
        type=str,
        help="last 3 digits of the serial number",
        default=None,
    )
    parser.add_argument(
        "-d",
        "--interval"
    )

    args = parser.parse_args()
    main(args.identifier)