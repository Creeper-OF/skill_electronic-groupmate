#!/usr/bin/env python3
"""Export draft meme entries to markdown review sheets grouped by category."""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
from typing import Any


DEFAULT_ROOT = pathlib.Path(__file__).resolve().parents[1].parent / "electronic-groupmate-crawl-data"


def load_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_category(path: pathlib.Path, category: str, rows: list[dict[str, Any]]) -> None:
    lines = [f"# Review: {category}", ""]
    for index, row in enumerate(rows, 1):
        meta = row.get("draft_meta", {})
        aliases = ", ".join(row.get("aliases", []))
        keywords = ", ".join(row.get("keywords", [])[:10])
        sources = ", ".join(row.get("source_urls", []))
        lines.extend(
            [
                f"## {index}. {row['name']}",
                "",
                f"- id: `{row['id']}`",
                f"- category: `{row['category']}`",
                f"- review_status: `{row['review_status']}`",
                f"- risk/intensity: `{row['risk']}` / `{row['intensity']}`",
                f"- tier/heat: `{meta.get('tier', '')}` / `{meta.get('heat', '')}`",
                f"- aliases: {aliases or '-'}",
                f"- keywords: {keywords or '-'}",
                f"- summary: {row.get('summary', '')}",
                f"- example: {row.get('example_usage', [''])[0]}",
                f"- source_urls: {sources or '-'}",
                "",
                "Review notes:",
                "",
                "- [ ] category ok",
                "- [ ] summary rewritten",
                "- [ ] suitable/unsuitable ok",
                "- [ ] example usable",
                "- [ ] risk ok",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(DEFAULT_ROOT / "classified" / "draft-meme-entries.jsonl"),
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_ROOT / "review"))
    parser.add_argument("--limit-per-category", type=int, default=30)
    args = parser.parse_args()

    rows = load_jsonl(pathlib.Path(args.input))
    grouped: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for category, category_rows in sorted(grouped.items()):
        category_rows = category_rows[: args.limit_per_category]
        write_category(out_dir / f"{category}-review.md", category, category_rows)
        print(f"Wrote {len(category_rows)} rows for {category}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
