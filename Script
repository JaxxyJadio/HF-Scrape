import argparse, json, re, sys
from datasets import load_dataset, DatasetDict, IterableDataset
from typing import List, Optional, Set

WS_RE = re.compile(r"\s+")

def normalize(s: str, squeeze_ws: bool=True, strip: bool=True, lower: bool=False) -> str:
    if s is None:
        return ""
    if strip:
        s = s.strip()
    if squeeze_ws:
        s = WS_RE.sub(" ", s)
    if lower:
        s = s.lower()
    return s

def build_input(example: dict, cols: List[str], sep: str, template: Optional[str]) -> Optional[str]:
    try:
        if template:
            # Use Python format with the example dict as context
            return template.format(**example)
        parts = []
        for c in cols:
            v = example.get(c, "")
            if v is None:
                v = ""
            if not isinstance(v, str):
                v = str(v)
            if v:
                parts.append(v)
        return sep.join(parts)
    except Exception:
        return None

def main():
    p = argparse.ArgumentParser(description="Scrape HF dataset and emit JSONL with only an 'input' field.")
    p.add_argument("--dataset", required=True, help="repo id or path, e.g. openwebtext, tatsu-lab/alpaca")
    p.add_argument("--split", default="train", help="dataset split, e.g. train, validation, test")
    p.add_argument("--config", default=None, help="dataset config name if needed")
    p.add_argument("--cols", default=None, help="comma-separated text columns to concatenate (default: auto-detect)")
    p.add_argument("--sep", default=" ", help="separator used when concatenating cols")
    p.add_argument("--template", default=None,
                   help="optional format template, e.g. '{instruction}\n{input}\n{output}' "
                        "Only keys present in the row are usable. Result still stored under 'input'.")
    p.add_argument("--min_chars", type=int, default=1, help="drop rows with fewer characters")
    p.add_argument("--max_chars", type=int, default=200000, help="drop rows with more characters")
    p.add_argument("--lower", action="store_true", help="lowercase normalized text before filtering/dedup")
    p.add_argument("--dedup", action="store_true", help="deduplicate by normalized text")
    p.add_argument("--limit", type=int, default=None, help="max number of rows to write")
    p.add_argument("--streaming", action="store_true", help="use streaming mode (iterates without full download)")
    p.add_argument("--trust_remote_code", action="store_true", help="pass through to load_dataset when needed")
    p.add_argument("--out", required=True, help="output JSONL path")
    args = p.parse_args()

    # Load split
    ds = load_dataset(
        args.dataset,
        args.config,
        split=args.split,
        streaming=args.streaming,
        trust_remote_code=args.trust_remote_code,
    )

    # Auto-detect columns if not provided
    if args.cols:
        cols = [c.strip() for c in args.cols.split(",") if c.strip()]
    else:
        # Heuristic: prefer common text cols, else all string cols
        common = ["text", "content", "sentence", "prompt", "instruction", "question", "input"]
        available = list(ds.features.keys()) if not isinstance(ds, IterableDataset) else None
        if available:
            cols = [c for c in common if c in available]
            if not cols:
                # Fall back to all non-numeric string-like columns
                cols = [c for c, f in ds.features.items() if getattr(f, "dtype", "").startswith("string")]
            if not cols:
                print("Could not infer text columns. Provide --cols.", file=sys.stderr)
                sys.exit(2)
        else:
            # In streaming mode, we cannot see features reliably; try the common list and hope
            cols = common

    seen: Set[str] = set() if args.dedup else None
    n_written = 0

    with open(args.out, "w", encoding="utf-8") as fout:
        it = ds if isinstance(ds, IterableDataset) else (r for r in ds)
        for ex in it:
            s = build_input(ex, cols, args.sep, args.template)
            if not s:
                continue
            s_norm = normalize(s, squeeze_ws=True, strip=True, lower=args.lower)
            if len(s_norm) < args.min_chars or len(s_norm) > args.max_chars:
                continue
            if args.dedup:
                if s_norm in seen:
                    continue
                seen.add(s_norm)
            # Emit only {"input": "..."}
            fout.write(json.dumps({"input": s_norm}, ensure_ascii=False) + "\n")
            n_written += 1
            if args.limit and n_written >= args.limit:
                break

    print(f"Wrote {n_written} rows to {args.out}")

if __name__ == "__main__":
    main()
