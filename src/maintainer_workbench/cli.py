from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model import WorkItem
from .triage import classify_item, render_digest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maintainer-workbench",
        description="Generate maintainer triage digests from GitHub issue and PR metadata.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    digest = subparsers.add_parser("digest", help="Generate a Markdown triage digest.")
    digest.add_argument("input", type=Path, help="Path to a JSON array of issue or PR items.")
    digest.add_argument("-o", "--output", type=Path, help="Write the digest to a Markdown file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "digest":
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        items = [WorkItem.from_json(entry) for entry in payload]
        digest = render_digest([classify_item(item) for item in items])
        if args.output:
            args.output.write_text(digest, encoding="utf-8")
        else:
            print(digest, end="")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
