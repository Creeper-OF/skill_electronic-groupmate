# Meme Entry Format

Store final reviewed entries as JSON objects or JSONL records. JSON is preferred for script validation.

Entries are usage guides. They teach meaning, fit, risk, and example phrasing. They do not require the model to use the expression, and they should not be sampled randomly.

Required fields:

```json
{
  "id": "anime-mygo-band-forever",
  "name": "一辈子组乐队",
  "aliases": ["一辈子乐队"],
  "category": "anime",
  "source_circle": "MyGO!!!!! / ACGN community",
  "summary": "A short rewritten explanation of what the meme means.",
  "keywords": ["死循环", "长期绑定", "无法退出"],
  "trigger_contexts": ["loop without exit condition", "long-running repeated task"],
  "suitable": ["low-risk debugging after root cause is confirmed"],
  "unsuitable": ["formal reports", "user is upset", "real relationship conflict"],
  "usage_style": ["analogy", "paraphrase"],
  "freshness": "evergreen",
  "intensity": 2,
  "risk": "low",
  "requires_user_familiarity": true,
  "example_usage": ["这个循环没退出条件，有点一辈子组乐队了。"],
  "source_urls": ["https://zh.moegirl.org.cn/..."],
  "license_note": "Source candidate from Moegirlpedia; final summary and example are rewritten. Keep attribution and non-commercial/share-alike constraints in mind.",
  "review_status": "reviewed",
  "last_reviewed": "2026-06-10"
}
```

Allowed values:

- `category`: `general`, `anime`, `guichu`, `games`, `vtuber`, `tuwei`, `bad_memes`, `swears`, `roasts`, `dark_humor`, `shitpost`.
- `usage_style`: `direct_quote`, `paraphrase`, `structural_meme`, `reaction_phrase`, `analogy`.
- `freshness`: `current`, `recent`, `evergreen`, `nostalgic`, `stale`, `retired`.
- `risk`: `low`, `medium`, `high`.
- `review_status`: `draft`, `needs_review`, `reviewed`, `retired`.
- `intensity`: integer from 0 to 5.

Avoid long copyrighted quotes. Prefer short rewritten summaries, keywords, usage constraints, and source URLs.

Before using an entry, verify that the current reply actually benefits from that expression. If plain Chinese is smoother, do not use the entry.

Optional fields for `swears`:

- `severity`: `mild`, `medium`, `strong`.
- `target_policy`: describe what it may target, such as `situation_only`, `self_directed`, or `never_target_user`.
- `profanity_role`: `emotion_marker`, `intensifier`, `situation_roast`, or `direct_insult`.

Reviewed entries should not use `direct_insult` unless there is a narrow, clearly safe quoting or analysis purpose.

Optional fields for `roasts`:

- `roast_formula`: reusable pattern, such as `your_operation_is_like_x_because_y`.
- `deescalation`: short phrase to soften or walk back the roast.
- `target_policy`: same idea as `swears`; prefer `operation_or_situation`.

Reviewed roast entries must be playful, absurd, and reversible. Avoid fixed insults that reduce to "you are stupid".
