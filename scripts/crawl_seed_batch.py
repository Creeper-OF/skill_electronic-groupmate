#!/usr/bin/env python3
"""Run a small seed crawl for electronic-groupmate candidate data."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import time

from fetch_moegirl_candidates import (
    API_URL as MOEGIRL_API_URL,
    DEFAULT_USER_AGENT,
    fetch_extract,
    fetch_wikitext,
    search_pages,
)


WIKTIONARY_API_URL = "https://zh.wiktionary.org/w/api.php"

SEEDS = [
    # category, source, api_url, query, slug
    ("anime", "moegirlpedia", MOEGIRL_API_URL, "MyGO", "mygo"),
    ("anime", "moegirlpedia", MOEGIRL_API_URL, "Re:0", "rezero"),
    ("anime", "moegirlpedia", MOEGIRL_API_URL, "孤独摇滚", "bocchi"),
    ("anime", "moegirlpedia", MOEGIRL_API_URL, "JOJO", "jojo"),
    ("anime", "moegirlpedia", MOEGIRL_API_URL, "BanG Dream", "bang-dream"),
    ("guichu", "moegirlpedia", MOEGIRL_API_URL, "金坷垃", "jinkela"),
    ("guichu", "moegirlpedia", MOEGIRL_API_URL, "诸葛亮", "zhuge-liang"),
    ("guichu", "moegirlpedia", MOEGIRL_API_URL, "王朗", "wang-lang"),
    ("guichu", "moegirlpedia", MOEGIRL_API_URL, "改革春风吹满地", "gaige-chunfeng"),
    ("guichu", "moegirlpedia", MOEGIRL_API_URL, "鬼畜全明星", "guichu-allstars"),
    ("games", "moegirlpedia", MOEGIRL_API_URL, "Minecraft", "minecraft"),
    ("games", "moegirlpedia", MOEGIRL_API_URL, "原神", "genshin"),
    ("games", "moegirlpedia", MOEGIRL_API_URL, "黑神话悟空", "black-myth-wukong"),
    ("games", "moegirlpedia", MOEGIRL_API_URL, "赛博朋克2077", "cyberpunk-2077"),
    ("games", "moegirlpedia", MOEGIRL_API_URL, "Steam", "steam"),
    ("vtuber", "moegirlpedia", MOEGIRL_API_URL, "虚拟主播", "vtuber"),
    ("vtuber", "moegirlpedia", MOEGIRL_API_URL, "Hololive", "hololive"),
    ("vtuber", "moegirlpedia", MOEGIRL_API_URL, "彩虹社", "nijisanji"),
    ("tuwei", "moegirlpedia", MOEGIRL_API_URL, "土味情话", "tuwei-love"),
    ("tuwei", "moegirlpedia", MOEGIRL_API_URL, "精神小伙", "spirit-boy"),
    ("bad_memes", "moegirlpedia", MOEGIRL_API_URL, "奶龙", "nailong"),
    ("bad_memes", "moegirlpedia", MOEGIRL_API_URL, "鸡你太美", "ji-ni-tai-mei"),
    ("bad_memes", "moegirlpedia", MOEGIRL_API_URL, "抽象话", "abstract-speech"),
    ("swears", "zh-wiktionary", WIKTIONARY_API_URL, "草", "cao"),
    ("swears", "zh-wiktionary", WIKTIONARY_API_URL, "卧槽", "wo-cao"),
    ("swears", "zh-wiktionary", WIKTIONARY_API_URL, "靠", "kao"),
    ("swears", "zh-wiktionary", WIKTIONARY_API_URL, "麻了", "ma-le"),
    ("swears", "zh-wiktionary", WIKTIONARY_API_URL, "菜", "cai"),
]

CATEGORY_LABELS = {
    "anime": "anime",
    "guichu": "guichu",
    "games": "games",
    "vtuber": "vtuber",
    "tuwei": "tuwei",
    "bad_memes": "bad_memes",
    "swears": "swears",
}


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return cleaned or "query"


def fetch_seed(
    api_url: str,
    source: str,
    category: str,
    query: str,
    limit: int,
    delay: float,
    max_text_chars: int,
    user_agent: str,
) -> list[dict]:
    rows = []
    for item in search_pages(api_url, query, limit, user_agent)[:limit]:
        page = fetch_extract(api_url, item["title"], user_agent)
        text = page.get("extract", "")
        text_kind = "extract"
        if not text:
            text = fetch_wikitext(api_url, item["title"], user_agent)
            text_kind = "wikitext"
        if max_text_chars > 0:
            text = text[:max_text_chars]
        rows.append(
            {
                "source": source,
                "category_hint": category,
                "query": query,
                "pageid": page.get("pageid"),
                "title": page.get("title", item.get("title")),
                "url": page.get("fullurl", item.get("url")),
                "text_kind": text_kind,
                "extract": text,
                "categories": [cat.get("title") for cat in page.get("categories", [])],
            }
        )
        time.sleep(max(delay, 0))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=str(pathlib.Path(__file__).resolve().parents[1].parent / "electronic-groupmate-crawl-data"),
        help="crawl data root",
    )
    parser.add_argument("--limit", type=int, default=3, help="pages per seed query")
    parser.add_argument("--delay", type=float, default=0.25, help="seconds between page fetches")
    parser.add_argument("--max-text-chars", type=int, default=5000)
    parser.add_argument("--only", choices=sorted(CATEGORY_LABELS), help="crawl only one category")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    args = parser.parse_args()

    root = pathlib.Path(args.root)
    raw_root = root / "raw"
    logs_root = root / "logs"
    raw_root.mkdir(parents=True, exist_ok=True)
    logs_root.mkdir(parents=True, exist_ok=True)

    summary = []
    selected = [seed for seed in SEEDS if args.only is None or seed[0] == args.only]
    for category, source, api_url, query, slug in selected:
        label = CATEGORY_LABELS[category]
        category_dir = raw_root / label
        category_dir.mkdir(parents=True, exist_ok=True)
        out_path = category_dir / f"{source}__{safe_filename(slug)}.jsonl"
        try:
            rows = fetch_seed(
                api_url,
                source,
                category,
                query,
                args.limit,
                args.delay,
                args.max_text_chars,
                args.user_agent,
            )
            with out_path.open("w", encoding="utf-8") as handle:
                for row in rows:
                    handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            status = "ok"
        except Exception as exc:  # noqa: BLE001 - batch crawl should keep moving.
            rows = []
            status = f"error: {exc}"
        summary.append({"category": category, "source": source, "query": query, "rows": len(rows), "out": str(out_path), "status": status})
        print(f"{category}/{source}/{query}: {len(rows)} rows ({status})", file=sys.stderr)

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary_path = logs_root / f"seed-crawl-summary-{timestamp}.jsonl"
    latest_path = logs_root / "seed-crawl-summary-latest.jsonl"
    with summary_path.open("w", encoding="utf-8") as handle:
        for row in summary:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    with latest_path.open("w", encoding="utf-8") as handle:
        for row in summary:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(f"Wrote summary to {summary_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
