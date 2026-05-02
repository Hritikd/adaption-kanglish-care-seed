# Results

Expansion run completed on the 57-row Kanglish customer support seed using Adaption's Adaptive Data product (Localize mode, 50% slider, 2.5× multiplier, 3 markets: Spain, Indonesia, Brazil).

Output: `expanded.jsonl`, 139 rows, all tagged `kn-en` / `kanglish`. Domain distribution preserved across the original 7 domains (ecommerce, payments, food delivery, ride hailing, telecom, banking, health appointments).

## Adaption's own quality grade

The platform's internal evaluator graded the expanded dataset against the seed:

| Metric | Before | After |
|---|---|---|
| Quality score | 6.0 | 7.9 |
| Grade | C | B |
| Percentile | 8.4 | 16.7 |

Reported relative improvement: **31.7%**.

This is Adaption's self-evaluation, not an independent benchmark. Useful as a directional signal, not as ground truth.

## Three findings worth flagging

### 1. Blueprint preserved Kanglish on tagged rows

The original concern was that expansion would regress to monolingual English. It didn't. Sample row from the expanded set:

> **Original prompt:** `wallet balance show aagtilla home screen alli, refresh maadidru same payments_upi complaint`
> **Enhanced completion:** *"Hey, wallet balance update aagtilla andre really sorry for the trouble! Sometimes UPI sync aagoke time thogolluthe or just display issue irthade. App cache clear maadi, restart maadi nodi..."*

The Blueprint's split between Preservation directives and Generation directives appears to have done what it claimed: the model held onto Kanglish constructions (`aagtilla`, `irthade`, `thogolluthe`, `maadi nodi`) instead of normalizing them away.

### 2. Localization mode produces cross-lingual training pairs, not target-language replacements

This was unexpected. With Spain/Indonesia/Brazil set as localization markets, I assumed the run would produce Spanish, Indonesian, and Portuguese rows alongside the Kanglish base. What actually happened: a meaningful fraction of expanded rows have prompts in the target language (Portuguese/Spanish/Indonesian) but completions still in Kanglish.

Example:

> **Prompt (Portuguese):** "Preciso atualizar meu KYC, mudei de endereço para Bangalore."
> **Enhanced completion (Kanglish):** *"Namaskara. Nanna address recent aagi Bangalore ge change aagide, adakke nanna bank account nalli KYC details update madikollalu ichchisuttene..."*

This isn't necessarily a bug. Cross-lingual prompt → response pairs are genuinely useful for some tasks (multilingual customer support routing, for example). But it's a different artifact than what the localization label suggests, and worth knowing about before relying on it.

### 3. Pricing was the surprise

Full run, including Blueprint-structured prompt, 3-market localization, hallucination mitigation, and 2.5× expansion: **2 credits**. For an early-access tier, that's well below what running a comparable synthetic data pipeline through OpenAI or Anthropic APIs would cost. The unit cost of adaptation, in dollar terms, looks like the right shape.

## One observation about the diagnosis stage

Adaption's automatic language detection on the seed identified it as roughly 96% English with traces of Dutch and Portuguese. There is no Dutch or Portuguese in the seed, and the dataset is Kannada-English code-mixed. This is a representative long-tail case: the auto-detector was working off a feature distribution where Roman-script Kanglish doesn't have a native bucket, so it fell into the nearest neighbours. Worth flagging as the exact kind of gap an India-focused ambassador run could help close.

## What's next

Three things I'd want to run on top of this data:

1. **Context-column ablation.** Run the same seed without the `domain`, `intent`, and `code_mix_type` context columns, to isolate how much of the Kanglish preservation is coming from the Blueprint itself versus the structural metadata.
2. **Domain steerability test.** Take a single Kanglish prompt and run it through the platform with each of the 7 domain tags, to measure how much the response register actually shifts.
3. **Downstream fine-tuning eval.** Take Llama 3 8B, fine-tune on a held-out split, and measure whether the expanded data produces real lift on a Kanglish customer-support task vs. the seed alone. Small enough to run on a single H100 via Unsloth.

The dataset itself is useful, but item 3 is what would actually validate whether the generated data improves downstream model performance.

## Reproducibility

The exact run can be reproduced via `expand.py` in this repo:

```bash
export ADAPTION_API_KEY=pt_live_...
python expand.py --seed seed.jsonl --out expanded.jsonl
```

See `docs/methodology.md` for schema, design rationale, and evaluation criteria.
