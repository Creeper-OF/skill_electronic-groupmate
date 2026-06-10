#!/usr/bin/env python3
"""Crawl candidate pages linked from Moegirlpedia seed/list pages."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
import time
import urllib.parse

from fetch_moegirl_candidates import (
    API_URL as MOEGIRL_API_URL,
    DEFAULT_USER_AGENT,
    fetch_extract,
    fetch_wikitext,
    request_json,
)


def title_from_url_or_text(value: str) -> str:
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urllib.parse.urlparse(value)
        title = urllib.parse.unquote(parsed.path.rsplit("/", 1)[-1])
    else:
        title = value
    return title.replace("_", " ").strip()


def safe_filename(value: str) -> str:
    ascii_part = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    if ascii_part:
        return f"{ascii_part[:64]}-{digest}"
    encoded = urllib.parse.quote(value, safe="")
    return f"{encoded[:64]}-{digest}" or f"seed-{digest}"


def fetch_links(api_url: str, title: str, user_agent: str, max_links: int) -> list[str]:
    links: list[str] = []
    params: dict[str, str | int] = {
        "action": "query",
        "titles": title,
        "prop": "links",
        "plnamespace": 0,
        "pllimit": "max",
    }
    while True:
        payload = request_json(api_url, params, user_agent)
        pages = payload.get("query", {}).get("pages", [])
        if pages:
            for item in pages[0].get("links", []):
                linked_title = item.get("title")
                if linked_title:
                    links.append(linked_title)
                    if len(links) >= max_links:
                        return links
        cont = payload.get("continue", {})
        if not cont or len(links) >= max_links:
            return links
        params.update(cont)


def fetch_candidate(
    api_url: str,
    title: str,
    source: str,
    category_hint: str,
    seed_title: str,
    depth: int,
    max_text_chars: int,
    user_agent: str,
) -> dict:
    page = fetch_extract(api_url, title, user_agent)
    text = page.get("extract", "")
    text_kind = "extract"
    if not text:
        text = fetch_wikitext(api_url, title, user_agent)
        text_kind = "wikitext"
    if max_text_chars > 0:
        text = text[:max_text_chars]
    return {
        "source": source,
        "category_hint": category_hint,
        "seed_title": seed_title,
        "depth": depth,
        "pageid": page.get("pageid"),
        "title": page.get("title", title),
        "url": page.get("fullurl"),
        "text_kind": text_kind,
        "extract": text,
        "categories": [cat.get("title") for cat in page.get("categories", [])],
    }


def read_seed_file(path: pathlib.Path) -> list[str]:
    values = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            values.append(stripped)
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-url", action="append", default=[], help="seed URL or title; repeatable")
    parser.add_argument("--seed-file", help="UTF-8 file containing one seed URL/title per line")
    parser.add_argument("--api-url", default=MOEGIRL_API_URL)
    parser.add_argument("--source", default="moegirlpedia")
    parser.add_argument("--category-hint", default="mixed")
    parser.add_argument(
        "--root",
        default=str(pathlib.Path(__file__).resolve().parents[1].parent / "electronic-groupmate-crawl-data"),
        help="crawl data root",
    )
    parser.add_argument("--depth", type=int, default=1, help="0 fetches seeds only; 1 fetches seed links")
    parser.add_argument("--max-links-per-seed", type=int, default=120)
    parser.add_argument("--max-pages", type=int, default=200, help="global page fetch cap")
    parser.add_argument("--max-pages-per-seed", type=int, default=40)
    parser.add_argument("--skip-existing", action="store_true", help="skip seed output files that already contain rows")
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--max-text-chars", type=int, default=5000)
    parser.add_argument("--include-regex", help="optional title include regex")
    parser.add_argument("--exclude-regex", help="optional title exclude regex")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    args = parser.parse_args()

    seeds = list(args.seed_url)
    if args.seed_file:
        seeds.extend(read_seed_file(pathlib.Path(args.seed_file)))
    if not seeds:
        parser.error("provide --seed-url or --seed-file")

    include_re = re.compile(args.include_regex) if args.include_regex else None
    exclude_re = re.compile(args.exclude_regex) if args.exclude_regex else None

    root = pathlib.Path(args.root)
    raw_root = root / "raw" / "link_graph"
    logs_root = root / "logs"
    raw_root.mkdir(parents=True, exist_ok=True)
    logs_root.mkdir(parents=True, exist_ok=True)

    fetched_titles: set[str] = set()
    summaries = []
    live_summary_path = logs_root / "link-graph-summary-live.jsonl"
    live_summary_path.write_text("", encoding="utf-8")

    for seed in seeds:
        seed_title = title_from_url_or_text(seed)
        out_path = raw_root / f"{args.source}__links__{safe_filename(seed_title)}.jsonl"
        if args.skip_existing and out_path.exists() and out_path.stat().st_size > 0:
            rows = sum(1 for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip())
            summary = {"seed": seed_title, "rows": rows, "out": str(out_path), "status": "skipped_existing"}
            summaries.append(summary)
            with live_summary_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(summary, ensure_ascii=True) + "\n")
            print(f"{seed_title}: skipped existing {rows} rows -> {out_path}", file=sys.stderr)
            continue

        queue: list[tuple[str, int]] = [(seed_title, 0)]
        if args.depth >= 1:
            linked = fetch_links(args.api_url, seed_title, args.user_agent, args.max_links_per_seed)
            queue.extend((title, 1) for title in linked)

        rows = 0
        with out_path.open("w", encoding="utf-8") as handle:
            for title, depth in queue:
                if len(fetched_titles) >= args.max_pages:
                    break
                if args.max_pages_per_seed > 0 and rows >= args.max_pages_per_seed:
                    break
                if title in fetched_titles:
                    continue
                if include_re and not include_re.search(title):
                    continue
                if exclude_re and exclude_re.search(title):
                    continue
                try:
                    row = fetch_candidate(
                        args.api_url,
                        title,
                        args.source,
                        args.category_hint,
                        seed_title,
                        depth,
                        args.max_text_chars,
                        args.user_agent,
                    )
                    handle.write(json.dumps(row, ensure_ascii=True) + "\n")
                    fetched_titles.add(title)
                    rows += 1
                    time.sleep(max(args.delay, 0))
                except Exception as exc:  # noqa: BLE001 - keep batch crawl moving.
                    print(f"error fetching {title}: {exc}", file=sys.stderr)
        summary = {"seed": seed_title, "rows": rows, "out": str(out_path), "status": "ok"}
        summaries.append(summary)
        with live_summary_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(summary, ensure_ascii=True) + "\n")
        print(f"{seed_title}: {rows} rows -> {out_path}", file=sys.stderr)
        if len(fetched_titles) >= args.max_pages:
            break

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary_path = logs_root / f"link-graph-summary-{timestamp}.jsonl"
    latest_path = logs_root / "link-graph-summary-latest.jsonl"
    for path in (summary_path, latest_path):
        with path.open("w", encoding="utf-8") as handle:
            for row in summaries:
                handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(f"Wrote summary to {summary_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
