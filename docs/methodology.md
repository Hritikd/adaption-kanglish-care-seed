# Methodology

This document describes how the seed dataset is structured, how Adaptive Data is used to expand it, and how quality is evaluated. It is meant to be read alongside `seed.jsonl` and `expand.py` in the repo root.

## Why this dataset exists

Frontier models are optimised for the average case. For most of India, the average case is a poor fit. Real users do not write in clean monolingual English, nor in clean monolingual Kannada. They code-switch — embedding English nouns and brand terms inside Kannada sentence structure, often in Roman script rather than the native script. Customer-support interactions are one of the highest-volume domains where this code-mixing happens, and one of the lowest-coverage domains in open training data.

This repo is a small, deliberate attempt to fill part of that gap, and to demonstrate the loop Adaption's Adaptive Data product was built for: a tightly-scoped, high-quality seed → automated expansion → a model-ready dataset that did not exist before.

## The seed

`seed.jsonl` is a hand-curated set of 57 code-mixed customer-support interactions across seven domains: ecommerce delivery, UPI payments, food delivery, ride hailing, telecom billing, banking, and health appointments. Each row has the following schema:

| field | type | required | notes |
|---|---|---|---|
| `id` | string | yes | stable identifier, format `[lang]-care-NNN` |
| `prompt` | string | yes | the user message, code-mixed, written the way real users type it |
| `completion` | string | yes | the support response, register-matched to the prompt |
| `language_primary` | string | yes | code-mix tag, e.g. `kn-en` for Kanglish |
| `domain` | string | yes | one of: `ecommerce_delivery`, `payments_upi`, `food_delivery`, `ride_hailing`, `telecom_billing`, `banking`, `health_appointments` |
| `code_mix_type` | string | yes | one of: `kanglish`, `hinglish`, `tanglish`, `tenglish`, `manglish`, `benglish` |
| `intent` | string | yes | one of: `track_order`, `refund_status`, `replace_item`, `cancel_order`, `payment_failed`, `agent_handoff`, `complaint`, `info_request` |
| `script` | string | yes | one of: `roman`, `native`, `mixed` |
| `register` | string | yes | one of: `casual`, `formal` — used to test register preservation through expansion |

Design choices worth noting:

- **Roman script is the default.** Most Indian users type in Roman script on phones, and most existing datasets are weighted toward native script. Reflecting actual user behaviour is more useful than reflecting linguistic ideals.
- **Register matching matters.** A casual prompt should get a warm, casual response; a formal complaint should get a measured, formal one. This is something the seed encodes explicitly so the expansion preserves it.
- **No PII.** All names, phone numbers, order IDs, and addresses are synthetic.

## The expansion

`expand.py` calls the Adaptive Data SDK with the column mapping below:

```python
COLUMN_MAPPING = {
    "prompt": "prompt",
    "completion": "completion",
    "context": ["language_primary", "domain", "code_mix_type", "intent"],
}
```

Passing the structural fields in `context` is intentional: it tells the adapter to treat them as conditioning signal rather than free-text noise, so the expanded rows preserve the code-mix ratio, intent, and domain distribution of the seed instead of regressing to monolingual English (which is the failure mode without this).

The script always runs `estimate=True` first to print expected credit consumption before committing the run. With 57 seed rows, expansion to roughly a 1,000-row training-ready set is the target. Final size depends on what the estimate returns and how many credits remain.

## Evaluation

A dataset is only useful if its quality is verifiable. The evaluation looks at four axes:

1. **Code-mix preservation.** What fraction of expanded prompts retain code-switching? A run that drops the code-mix ratio is a regression even if every row is fluent.
2. **Intent fidelity.** Does each expanded row still match its labelled intent? Sampled manually on a 50-row subset.
3. **Register match.** Does the completion register match the prompt register? Casual–casual, formal–formal.
4. **Factual safety.** Customer-support responses must not invent policies, refund timelines, or escalation paths. Spot-checked against the seed's stated assumptions.

Numerical results from the run will be appended to this doc as `RESULTS.md` once expansion completes.

## What this is not

This is a seed and a method. It is not a benchmark, not a finished training set, and not a substitute for human-labelled domain-specific data. The point is to demonstrate that a single person, in a single evening, can take a known long-tail data gap and turn it into something usable — provided the platform underneath them treats data as malleable rather than static.

That is the bet Adaption is making. This is one tiny test of it.
