#!/usr/bin/env python3
"""Validate electronic-groupmate meme entries stored as JSON or JSONL."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


REQUIRED = {
    "id",
    "name",
    "aliases",
    "category",
    "source_circle",
    "summary",
    "keywords",
    "trigger_contexts",
    "suitable",
    "unsuitable",
    "usage_style",
    "freshness",
    "intensity",
    "risk",
    "requires_user_familiarity",
    "example_usage",
    "source_urls",
    "license_note",
    "review_status",
    "last_reviewed",
}

CATEGORIES = {
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
FRESHNESS = {"current", "recent", "evergreen", "nostalgic", "stale", "retired"}
RISKS = {"low", "medium", "high"}
REVIEW = {"draft", "needs_review", "reviewed", "retired"}
USAGE = {"direct_quote", "paraphrase", "structural_meme", "reaction_phrase", "analogy"}
SEVERITY = {"mild", "medium", "strong"}
PROFANITY_ROLE = {"emotion_marker", "intensifier", "situation_roast", "direct_insult", "quoted_or_analysis"}


def load_entries(path: pathlib.Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    payload = json.loads(text)
    if isinstance(payload, list):
        return payload
    return [payload]


def require_list(entry: dict[str, Any], field: str, errors: list[str]) -> None:
    if not isinstance(entry.get(field), list) or not entry.get(field):
        errors.append(f"{entry.get('id', '<missing id>')}: {field} must be a non-empty list")


def validate(entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED - set(entry))
    if missing:
        errors.append(f"{entry.get('id', '<missing id>')}: missing fields: {', '.join(missing)}")

    if entry.get("category") not in CATEGORIES:
        errors.append(f"{entry.get('id', '<missing id>')}: invalid category")
    if entry.get("freshness") not in FRESHNESS:
        errors.append(f"{entry.get('id', '<missing id>')}: invalid freshness")
    if entry.get("risk") not in RISKS:
        errors.append(f"{entry.get('id', '<missing id>')}: invalid risk")
    if entry.get("review_status") not in REVIEW:
        errors.append(f"{entry.get('id', '<missing id>')}: invalid review_status")
    if not isinstance(entry.get("intensity"), int) or not 0 <= entry.get("intensity", -1) <= 5:
        errors.append(f"{entry.get('id', '<missing id>')}: intensity must be an integer from 0 to 5")
    if not isinstance(entry.get("requires_user_familiarity"), bool):
        errors.append(f"{entry.get('id', '<missing id>')}: requires_user_familiarity must be boolean")

    for field in [
        "aliases",
        "keywords",
        "trigger_contexts",
        "suitable",
        "unsuitable",
        "usage_style",
        "example_usage",
        "source_urls",
    ]:
        require_list(entry, field, errors)

    for style in entry.get("usage_style", []):
        if style not in USAGE:
            errors.append(f"{entry.get('id', '<missing id>')}: invalid usage_style {style!r}")

    if entry.get("risk") == "high" and entry.get("review_status") == "reviewed":
        errors.append(f"{entry.get('id', '<missing id>')}: high-risk entries should not be reviewed without manual exception")
    if entry.get("category") == "swears":
        if entry.get("severity") not in SEVERITY:
            errors.append(f"{entry.get('id', '<missing id>')}: swears entries need severity mild/medium/strong")
        if entry.get("profanity_role") not in PROFANITY_ROLE:
            errors.append(f"{entry.get('id', '<missing id>')}: swears entries need a valid profanity_role")
        if not entry.get("target_policy"):
            errors.append(f"{entry.get('id', '<missing id>')}: swears entries need target_policy")
        if entry.get("severity") == "strong" and entry.get("review_status") == "reviewed":
            errors.append(f"{entry.get('id', '<missing id>')}: strong profanity should stay needs_review by default")
        if entry.get("profanity_role") == "direct_insult" and entry.get("review_status") == "reviewed":
            errors.append(f"{entry.get('id', '<missing id>')}: direct insults should stay needs_review by default")
    if entry.get("category") == "roasts":
        if not entry.get("roast_formula"):
            errors.append(f"{entry.get('id', '<missing id>')}: roasts entries need roast_formula")
        if not entry.get("deescalation"):
            errors.append(f"{entry.get('id', '<missing id>')}: roasts entries need deescalation")
        if not entry.get("target_policy"):
            errors.append(f"{entry.get('id', '<missing id>')}: roasts entries need target_policy")
        if entry.get("requires_user_familiarity") is not True:
            errors.append(f"{entry.get('id', '<missing id>')}: roasts entries should require user familiarity")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="JSON or JSONL entry files")
    args = parser.parse_args()

    all_errors: list[str] = []
    count = 0
    for raw_path in args.paths:
        path = pathlib.Path(raw_path)
        for entry in load_entries(path):
            count += 1
            all_errors.extend(validate(entry))

    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        return 1

    print(f"Validated {count} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
