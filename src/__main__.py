"""CLI for opinionpulse."""
import sys, json, argparse
from .core import Opinionpulse

def main():
    parser = argparse.ArgumentParser(description="Multi-agent public opinion analysis assistant — track sentiment, narratives, and discourse shifts")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Opinionpulse()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.collect_data(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"opinionpulse v0.1.0 — Multi-agent public opinion analysis assistant — track sentiment, narratives, and discourse shifts")

if __name__ == "__main__":
    main()
