#!/usr/bin/env python3
"""Import MonloHua/geng-skill gengku.json into candidate JSONL records."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from typing import Any


DEFAULT_ROOT = pathlib.Path(__file__).resolve().parents[1].parent / "electronic-groupmate-crawl-data"
DEFAULT_SOURCE_URL = "https://github.com/MonloHua/geng-skill"


CATEGORY_PATTERNS = [
    ("anime", re.compile(r"动漫|番剧|二次元|ACG|声优|漫画|动画|JOJO|MyGO|孤独摇滚|白学", re.I)),
    ("guichu", re.compile(r"鬼畜|B站|bilibili|哔哩哔哩|全明星|金坷垃|诸葛亮|王朗", re.I)),
    ("games", re.compile(r"游戏|玩家|服务器|Mod|Steam|原神|Minecraft|赛博朋克|黑神话", re.I)),
    ("vtuber", re.compile(r"虚拟主播|VTuber|VUP|直播|切片|hololive|彩虹社", re.I)),
    ("swears", re.compile(r"脏话|粗口|傻屌|卧槽|我操|我靠|你妈|妈的|他妈", re.I)),
    ("roasts", re.compile(r"嘲讽|吐槽|阴阳怪气|调侃|找茬|质疑", re.I)),
    ("tuwei", re.compile(r"土味|精神小伙|快手|抖音|情话", re.I)),
    ("bad_memes", re.compile(r"烂梗|抽象|奶龙|鸡你太美|低幼", re.I)),
]

SWEAR_NAMES = {
    "草",
    "艹",
    "卧槽",
    "我操",
    "我靠",
    "靠",
    "妈的",
    "他妈",
    "踏马",
    "特么",
    "菜",
}


def guess_category(name: str, entry: dict[str, Any]) -> str:
    normalized_name = name.strip().lower()
    if normalized_name in SWEAR_NAMES:
        return "swears"
    haystack = "\n".join(
        str(entry.get(field) or "")
        for field in ("meaning", "usage", "source")
    )
    haystack = f"{name}\n{haystack}"
    for category, pattern in CATEGORY_PATTERNS:
        if pattern.search(haystack):
            return category
    return "mixed"


def split_related(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"\s*/\s*|、|，|,", value)
    return [part.strip() for part in parts if part.strip()]


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def convert_entry(name: str, entry: dict[str, Any], source_url: str, imported_at: str) -> dict[str, Any]:
    category_hint = guess_category(name, entry)
    related = split_related(str(entry.get("related") or ""))
    keywords = [name]
    keywords.extend(alias.strip() for alias in re.split(r"\s*/\s*|、", name) if alias.strip() and alias.strip() != name)
    keywords.extend(related[:8])

    return {
        "source": "geng-skill",
        "source_url": source_url,
        "source_record": "gengku.json",
        "imported_at": imported_at,
        "name": name,
        "aliases": [item for item in keywords[1:] if item],
        "category_hint": category_hint,
        "tier": entry.get("tier"),
        "heat": entry.get("heat"),
        "meaning": entry.get("meaning") or "",
        "usage": entry.get("usage") or "",
        "source_text": entry.get("source") or "",
        "hot_content": entry.get("hot_content") or "",
        "related": related,
        "candidate_notes": [
            "Imported from MonloHua/geng-skill as a popularity-ranked meme candidate.",
            "Needs electronic-groupmate model classification before entering reviewed meme libraries.",
        ],
        "target_schema": "meme-entry-format.md",
        "review_status": "candidate",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="path to gengku.json")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="crawl data root")
    parser.add_argument("--out", help="output JSONL path")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--min-tier", choices=["SSS", "SS", "S", "A", "B", "C"], help="keep only this tier or hotter")
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)
    data = load_json(input_path)
    imported_at = dt.datetime.now(dt.timezone.utc).isoformat()

    tier_order = {"SSS": 0, "SS": 1, "S": 2, "A": 3, "B": 4, "C": 5}
    max_rank = tier_order[args.min_tier] if args.min_tier else None

    root = pathlib.Path(args.root)
    out_path = pathlib.Path(args.out) if args.out else root / "candidates" / "geng-skill-candidates.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for name, entry in data.items():
        tier = entry.get("tier")
        if max_rank is not None and tier_order.get(tier, 99) > max_rank:
            continue
        rows.append(convert_entry(name, entry, args.source_url, imported_at))

    with out_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    print(f"Imported {len(rows)} candidates to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
