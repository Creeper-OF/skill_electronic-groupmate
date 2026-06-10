#!/usr/bin/env python3
"""Convert candidate meme records into schema-valid draft entries."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
from typing import Any


DEFAULT_ROOT = pathlib.Path(__file__).resolve().parents[1].parent / "electronic-groupmate-crawl-data"
VALID_CATEGORIES = {
    "general",
    "anime",
    "guichu",
    "games",
    "vtuber",
    "tuwei",
    "bad_memes",
    "swears",
    "roasts",
    "dark_humor",
    "shitpost",
}


def slugify(value: str) -> str:
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"{ascii_part}-{digest}" if ascii_part else digest


def split_name_aliases(name: str, aliases: list[str]) -> list[str]:
    found: list[str] = []
    for value in [name, *aliases]:
        for part in re.split(r"\s*/\s*|、|，|,", value):
            part = part.strip()
            if part and part != name and part not in found:
                found.append(part)
    return found[:12]


def as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def normalize_category(category_hint: str) -> str:
    if category_hint in VALID_CATEGORIES and category_hint != "dark_humor":
        return category_hint
    return "general"


def freshness_from_tier(tier: str) -> str:
    if tier in {"SSS", "SS", "S"}:
        return "recent"
    if tier in {"A", "B"}:
        return "evergreen"
    return "nostalgic"


def intensity_for(category: str) -> int:
    if category == "swears":
        return 2
    if category == "roasts":
        return 3
    if category in {"bad_memes", "shitpost"}:
        return 3
    return 2


def risk_for(category: str) -> str:
    if category in {"swears", "roasts"}:
        return "medium"
    return "low"


def usage_style_for(category: str) -> list[str]:
    if category == "swears":
        return ["reaction_phrase"]
    if category == "roasts":
        return ["analogy", "paraphrase"]
    return ["reaction_phrase", "paraphrase"]


def source_urls_for(candidate: dict[str, Any]) -> list[str]:
    urls = []
    for key in ("source_url", "url"):
        value = candidate.get(key)
        if isinstance(value, str) and value.strip():
            urls.append(value.strip())
    return urls or ["local:candidate-import"]


def build_draft(candidate: dict[str, Any], now: str) -> dict[str, Any]:
    name = str(candidate.get("name") or candidate.get("title") or "").strip()
    aliases = split_name_aliases(name, as_list(candidate.get("aliases")))
    category = normalize_category(str(candidate.get("category_hint") or "general"))
    meaning = str(candidate.get("meaning") or candidate.get("extract") or "").strip()
    summary = meaning[:220] if meaning else f"候选梗「{name}」，需要复审后补充含义和使用场景。"
    related = as_list(candidate.get("related"))
    keywords = []
    for item in [name, *aliases, *related[:8]]:
        if item and item not in keywords:
            keywords.append(item)

    entry = {
        "id": f"{category}-{slugify(name)}",
        "name": name,
        "aliases": aliases or [name],
        "category": category,
        "source_circle": str(candidate.get("source_text") or candidate.get("source") or "Chinese internet"),
        "summary": summary,
        "keywords": keywords or [name],
        "trigger_contexts": [
            "low-risk informal Chinese conversation",
            "user tone permits meme-aware expression",
        ],
        "suitable": [
            "casual chat after the useful answer is clear",
            "lightweight reaction or analogy",
        ],
        "unsuitable": [
            "formal documents",
            "user is upset",
            "security, money, privacy, data loss, or other high-risk contexts",
        ],
        "usage_style": usage_style_for(category),
        "freshness": freshness_from_tier(str(candidate.get("tier") or "")),
        "intensity": intensity_for(category),
        "risk": risk_for(category),
        "requires_user_familiarity": category not in {"general", "swears"},
        "example_usage": [
            f"这里可以根据语境使用「{name}」，但需要复审后补一个更贴合的例句。"
        ],
        "source_urls": source_urls_for(candidate),
        "license_note": "候选资料来自外部抓取或导入；本条目为草稿，需要复审、改写示例并确认来源。",
        "review_status": "needs_review",
        "last_reviewed": now[:10],
        "draft_meta": {
            "source": candidate.get("source"),
            "tier": candidate.get("tier"),
            "heat": candidate.get("heat"),
            "hot_content": candidate.get("hot_content"),
            "imported_at": candidate.get("imported_at"),
        },
    }

    if category == "swears":
        entry.update(
            {
                "severity": "mild",
                "target_policy": "situation_only",
                "profanity_role": "emotion_marker",
            }
        )
    if category == "roasts":
        entry.update(
            {
                "roast_formula": "situation_or_operation_is_like_absurd_scene",
                "deescalation": "骂归骂，问题不大，先按修法来。",
                "target_policy": "operation_or_situation",
            }
        )
    return entry


def load_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(DEFAULT_ROOT / "candidates" / "geng-skill-candidates.jsonl"),
        help="candidate JSONL input",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_ROOT / "classified" / "draft-meme-entries.jsonl"),
        help="draft meme entry JSONL output",
    )
    parser.add_argument("--limit", type=int, default=120)
    parser.add_argument("--min-tier", choices=["SSS", "SS", "S", "A", "B", "C"], default="SS")
    args = parser.parse_args()

    tier_rank = {"SSS": 0, "SS": 1, "S": 2, "A": 3, "B": 4, "C": 5}
    max_rank = tier_rank[args.min_tier]
    candidates = load_jsonl(pathlib.Path(args.input))
    candidates = [
        item for item in candidates
        if item.get("name") and tier_rank.get(str(item.get("tier")), 99) <= max_rank
    ]
    candidates.sort(key=lambda item: float(item.get("heat") or 0), reverse=True)
    selected = candidates[: args.limit]

    now = dt.datetime.now(dt.timezone.utc).isoformat()
    seen_ids: set[str] = set()
    drafts = []
    for candidate in selected:
        draft = build_draft(candidate, now)
        base_id = draft["id"]
        suffix = 2
        while draft["id"] in seen_ids:
            draft["id"] = f"{base_id}-{suffix}"
            suffix += 1
        seen_ids.add(draft["id"])
        drafts.append(draft)

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for draft in drafts:
            handle.write(json.dumps(draft, ensure_ascii=False) + "\n")

    print(f"Wrote {len(drafts)} draft entries to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
