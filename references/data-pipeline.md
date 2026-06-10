# Data Pipeline

The crawler does not create final runtime entries. It creates candidates.

## Flow

```text
source API
  -> raw candidate cache
  -> external candidate imports
  -> model extraction
  -> model classification
  -> human or focused review
  -> reviewed JSONL library
  -> runtime category indexes
```

## Candidate Record

Raw candidates should keep:

- `title`
- `pageid`
- `url`
- `extract` or short source text
- `categories` if available
- `fetched_at`
- `source`

External candidate imports, such as `MonloHua/geng-skill`, should keep original popularity fields and source metadata, then pass through the same model classification/review gate as crawled candidates.

## Model Extraction

Extract:

- meme name and aliases
- source circle and work/community
- rewritten short summary
- keywords
- possible trigger contexts
- possible unsuitable contexts
- risk and intensity guesses
- source URLs and license note

The model should mark uncertain fields instead of inventing certainty.

## Review Gate

Only `review_status: reviewed` entries should be used in normal responses.

Automatically mark as `needs_review` when:

- risk is medium or high
- category is `dark_humor`
- category is `swears` and severity is `strong`
- profanity is a direct insult, identity slur, or targets a real person
- category is `roasts` and the target is the user's identity, intelligence, body, family, illness, or other personal trait
- usage requires direct quote
- source text is mostly plot, character biography, or long copyrighted line
- the model cannot name a concrete suitable context

## Source And License Notes

For Moegirlpedia-derived candidates, keep the original page URL. Do not paste large source passages into final entries. Use rewritten summaries and examples.

For `geng-skill` imports, treat `tier` and `heat` as popularity priors. Do not directly promote imported records into runtime meme libraries; first classify them into the project schema and review suitability, risk, intensity, and usage context.
