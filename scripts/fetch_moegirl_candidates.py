#!/usr/bin/env python3
"""Fetch conservative candidate pages from a MediaWiki API.

Defaults target Moegirlpedia. Use --api-url and --source for other MediaWiki
sources such as Wiktionary when curating profanity candidates.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.parse
import urllib.error
import urllib.request


API_URL = "https://zh.moegirl.org.cn/api.php"
DEFAULT_USER_AGENT = "electronic-groupmate-skill/0.1 (+local curation; contact: local)"


def request_json(api_url: str, params: dict[str, str | int], user_agent: str, retries: int = 3) -> dict:
    query = urllib.parse.urlencode({**params, "format": "json", "formatversion": "2"})
    req = urllib.request.Request(
        f"{api_url}?{query}",
        headers={"User-Agent": user_agent},
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt >= retries:
                raise
            retry_after = exc.headers.get("Retry-After")
            wait = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
            time.sleep(max(wait, 1))
    raise RuntimeError("unreachable retry loop")


def search_pages(api_url: str, query: str, limit: int, user_agent: str) -> list[dict]:
    payload = request_json(
        api_url,
        {
            "action": "opensearch",
            "search": query,
            "limit": min(limit, 50),
            "namespace": 0,
        },
        user_agent,
    )
    titles = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    urls = payload[3] if isinstance(payload, list) and len(payload) > 3 else []
    return [{"title": title, "url": urls[index] if index < len(urls) else None} for index, title in enumerate(titles)]


def fetch_extract(api_url: str, title: str, user_agent: str) -> dict:
    payload = request_json(
        api_url,
        {
            "action": "query",
            "prop": "extracts|categories|info",
            "titles": title,
            "explaintext": 1,
            "exintro": 1,
            "cllimit": 20,
            "inprop": "url",
        },
        user_agent,
    )
    pages = payload.get("query", {}).get("pages", [])
    return pages[0] if pages else {}


def fetch_wikitext(api_url: str, title: str, user_agent: str) -> str:
    payload = request_json(
        api_url,
        {
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "rvprop": "content",
            "rvslots": "*",
        },
        user_agent,
    )
    pages = payload.get("query", {}).get("pages", [])
    if not pages:
        return ""
    revisions = pages[0].get("revisions", [])
    if not revisions:
        return ""
    slots = revisions[0].get("slots", {})
    main = slots.get("main", {})
    return main.get("content", "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="MediaWiki search query, for example: MyGO")
    parser.add_argument("--api-url", default=API_URL, help="MediaWiki api.php URL")
    parser.add_argument("--source", default="moegirlpedia", help="source label stored in output rows")
    parser.add_argument("--limit", type=int, default=10, help="maximum search results, capped by API page size")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds to wait between page fetches")
    parser.add_argument("--max-text-chars", type=int, default=4000, help="maximum extract/wikitext characters per row")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--out", required=True, help="output JSONL path")
    args = parser.parse_args()

    fetched_at = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = []
    for item in search_pages(args.api_url, args.query, args.limit, args.user_agent)[: args.limit]:
        page = fetch_extract(args.api_url, item["title"], args.user_agent)
        extract = page.get("extract", "")
        text_kind = "extract"
        if not extract:
            extract = fetch_wikitext(args.api_url, item["title"], args.user_agent)
            text_kind = "wikitext"
        if args.max_text_chars > 0:
            extract = extract[: args.max_text_chars]
        rows.append(
            {
                "source": args.source,
                "fetched_at": fetched_at,
                "query": args.query,
                "pageid": page.get("pageid"),
                "title": page.get("title", item.get("title")),
                "url": page.get("fullurl", item.get("url")),
                "text_kind": text_kind,
                "extract": extract,
                "categories": [cat.get("title") for cat in page.get("categories", [])],
            }
        )
        time.sleep(max(args.delay, 0))

    with open(args.out, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    print(f"Wrote {len(rows)} candidates to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
