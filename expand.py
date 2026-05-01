"""
expand.py
---------
Run an Adaptive Data adaptation job against the seed dataset.

This script takes the small, hand-curated `seed.jsonl` and uses the
Adaption Python SDK to expand it into a larger, model-ready dataset.

Workflow (mirrors the lifecycle in the Adaption docs):
    1. ingest    : upload seed.jsonl
    2. estimate  : preview cost / duration before committing credits
    3. adapt     : start the run
    4. wait      : poll for completion
    5. export    : download the expanded dataset

Usage:
    export ADAPTION_API_KEY=pt_live_...
    python expand.py --seed seed.jsonl --out expanded.jsonl

Docs: https://docs.adaptionlabs.ai/introduction/getting-started/
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    from adaption import Adaption, DatasetTimeout
except ImportError:
    print(
        "[!] Adaption SDK not installed.\n"
        "    Run: pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


COLUMN_MAPPING = {
    # Required: the user query (code-mixed Indic input)
    "prompt": "prompt",
    # Optional but recommended: the support response
    "completion": "completion",
    # Optional context columns the adapter can use to preserve register,
    # domain, and code-mix characteristics during expansion.
    "context": ["language_primary", "domain", "code_mix_type", "intent"],
}


def load_api_key() -> str:
    key = os.environ.get("ADAPTION_API_KEY")
    if not key:
        print(
            "[!] ADAPTION_API_KEY not set.\n"
            "    Create a key at https://adaptionlabs.ai/app/settings\n"
            "    Then: export ADAPTION_API_KEY=pt_live_...",
            file=sys.stderr,
        )
        sys.exit(2)
    return key


def validate_seed(seed_path: Path) -> int:
    """Sanity-check the seed file before we spend credits on it."""
    if not seed_path.exists():
        print(f"[!] Seed file not found: {seed_path}", file=sys.stderr)
        sys.exit(3)

    required = {"prompt", "completion"}
    count = 0
    with seed_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"[!] Invalid JSON on line {i}: {e}", file=sys.stderr)
                sys.exit(4)
            missing = required - set(row.keys())
            if missing:
                print(
                    f"[!] Line {i} missing required fields: {missing}",
                    file=sys.stderr,
                )
                sys.exit(5)
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", default="seed.jsonl", help="Path to seed JSONL")
    parser.add_argument("--out", default="expanded.jsonl", help="Path to write expanded output")
    parser.add_argument(
        "--name",
        default=None,
        help="Dataset name on Adaption (default: seed filename)",
    )
    parser.add_argument(
        "--estimate-only",
        action="store_true",
        help="Only print estimated cost; do not start the run.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Seconds to wait for completion (default 1800 = 30 min).",
    )
    args = parser.parse_args()

    seed_path = Path(args.seed)
    out_path = Path(args.out)

    # 0. Validate locally before we touch the network
    n = validate_seed(seed_path)
    print(f"[+] Seed validated: {n} rows in {seed_path}")

    api_key = load_api_key()
    client = Adaption(api_key=api_key)

    # 1. Ingest
    print("[+] Uploading seed to Adaption...")
    upload = client.datasets.upload_file(
        str(seed_path),
        name=args.name or seed_path.stem,
    )
    dataset_id = upload.dataset_id
    print(f"    dataset_id = {dataset_id}")

    # Poll briefly until the row count surfaces (server-side processing)
    print("[+] Waiting for ingestion to settle...")
    for _ in range(30):
        status = client.datasets.get_status(dataset_id)
        if getattr(status, "row_count", None) is not None:
            print(f"    rows ingested: {status.row_count}")
            break
        time.sleep(2)

    # 2. Estimate (always do this — credits are finite)
    print("[+] Estimating run cost...")
    estimate = client.datasets.run(
        dataset_id,
        column_mapping=COLUMN_MAPPING,
        estimate=True,
    )
    print(f"    estimated credits: {estimate.estimated_credits_consumed}")
    print(f"    estimated minutes: {getattr(estimate, 'estimated_minutes', 'n/a')}")

    if args.estimate_only:
        print("[i] --estimate-only set; exiting before run.")
        return

    # 3. Adapt
    print("[+] Starting adaptation run...")
    run = client.datasets.run(
        dataset_id,
        column_mapping=COLUMN_MAPPING,
    )
    print(f"    run_id = {run.run_id}")

    # 4. Wait
    print(f"[+] Waiting for completion (timeout {args.timeout}s)...")
    try:
        final = client.datasets.wait_for_completion(dataset_id, timeout=args.timeout)
        print(f"    status = {final.status}")
        if getattr(final, "error", None):
            print(f"    error: {final.error.message}", file=sys.stderr)
    except DatasetTimeout as e:
        print(
            f"[!] Still running after {e.timeout}s "
            f"(last status: {e.last_status}). "
            f"You can re-run with --resume later.",
            file=sys.stderr,
        )
        sys.exit(6)

    # 5. Export
    print("[+] Fetching expanded dataset...")
    download_url = client.datasets.download(dataset_id)
    print(f"    presigned URL: {download_url}")
    print(f"    save it locally as: {out_path}")
    print(
        "\n[done] Expansion complete. "
        "Download the file above and commit it to data/expanded/ if you want it in the repo."
    )


if __name__ == "__main__":
    main()
