# Kanglish Care Seed

> A small, deliberate seed dataset for code-mixed Kannada–English customer support, built to test what happens when you take a known long-tail data gap and feed it through Adaptive Data.

**Status:** seed published. Expansion run pending — to be added as `expanded.jsonl` and `RESULTS.md` once complete.
**Built by:** Hritik Datta, from Bengaluru.
**Built with:** [Adaption](https://www.adaptionlabs.ai/) — Adaptive Data (early access).

---

## Why this exists

Most AI models work well until your use case doesn't fit. Then you're on your own.

For a large fraction of India, the use case doesn't fit. Real users don't write in clean monolingual English. They code-switch — slipping English nouns and brand names into Kannada sentence structure, typically in Roman script ("Kanglish"). Customer support is one of the highest-volume contexts where this happens, and one of the lowest-coverage contexts in open-source training data.

This repo is a small, honest attempt to fill part of that gap.

It is also a test of a thesis. Adaption argues that the bottleneck in AI right now isn't model size — it's the **unit cost of adaptation**. Their bet is that one person, working from a corner of the world that frontier labs have never optimised for, should be able to take a real data gap and close it without the budget, headcount, or month-long fine-tuning cycles that this kind of work used to demand.

This repo is one data point in that argument.

## What's here

```
.
├── README.md            ← you are here
├── seed.jsonl           ← 57 hand-curated code-mixed support interactions
├── expand.py            ← Adaptive Data SDK script: ingest → estimate → adapt → export
├── requirements.txt
├── LICENSE              ← MIT
└── docs/
    └── methodology.md   ← schema, expansion strategy, evaluation axes
```

## The seed

`seed.jsonl` contains 57 examples spread across 7 domains: ecommerce delivery, UPI payments, food delivery, ride hailing, telecom billing, banking, and health appointments. Each row is a code-mixed Kanglish customer message paired with a register-matched support response, plus structural metadata (domain, code-mix type, intent, script, register). See [`docs/methodology.md`](docs/methodology.md) for the full schema and design rationale.

A representative example:

```json
{
  "id": "kn-care-001",
  "prompt": "anna nanna order yelli ide? 3 days late aagide already, tracking update aagtilla",
  "completion": "Hi, sorry for the delay. Your order #ORD-48271 is currently at our Hosur sorting facility and will be out for delivery in the next 24 hours. We'll send you an SMS once the delivery partner picks it up.",
  "language_primary": "kn-en",
  "domain": "ecommerce_delivery",
  "code_mix_type": "kanglish",
  "intent": "track_order",
  "script": "roman",
  "register": "casual"
}
```

All names, phone numbers, order IDs, and addresses in the seed are synthetic. No PII.

## Reproducing the expansion

```bash
git clone https://github.com/<your-user>/adaption-kanglish-care-seed.git
cd adaption-kanglish-care-seed
pip install -r requirements.txt

export ADAPTION_API_KEY=pt_live_...

# Always estimate first
python expand.py --seed seed.jsonl --estimate-only

# Then run for real
python expand.py --seed seed.jsonl --out expanded.jsonl
```

The script wraps the documented Adaptive Data lifecycle: `upload_file → run (estimate) → run → wait_for_completion → download`. It passes `language_primary`, `domain`, `code_mix_type`, and `intent` as **context columns** during the run, which is the lever that keeps expanded rows from regressing to monolingual English. See [`expand.py`](expand.py) for the full call.

## Results

Will be filled in as `RESULTS.md` after the first expansion run completes. The quality axes the evaluation tracks (code-mix preservation, intent fidelity, register match, factual safety) are described in [`docs/methodology.md`](docs/methodology.md).

## What this is not

A benchmark. A finished training set. A substitute for human-labelled domain-specific data with native-speaker review.

What it is: an existence proof. One person, one evening, one underserved language pair, one platform that treats data as malleable. If the loop holds at this scale, it should hold for the much harder versions of the same problem — and that's the part that matters.

## About

I'm Hritik Datta, based in Bengaluru. I lead product at [Pre6.ai](https://pre6.ai), where we build application-layer AI software for manufacturers (backed by Peak XV and General Catalyst). 

This work was started as part of an application to the Adaption Ambassadors program and will continue regardless of the outcome — the gap it addresses is real either way.

If you want to use this seed, extend it to a language or vertical it doesn't yet cover, or talk about code-mixed Indic data work generally: open an issue, or reach me on LinkedIn.

## License

MIT. Use it, fork it, build on it. If it's useful, a citation is appreciated but not required.
