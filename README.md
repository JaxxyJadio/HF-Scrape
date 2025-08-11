# 1) Simple: take 'text' from openwebtext and write inputs
python hf_scrape_to_input_jsonl.py \
  --dataset openwebtext \
  --split train \
  --out /data/openwebtext_input.jsonl \
  --limit 200000 \
  --dedup

# 2) Multi-column concat: Alpaca-style
python hf_scrape_to_input_jsonl.py \
  --dataset tatsu-lab/alpaca \
  --split train \
  --cols instruction,input \
  --sep "\n\n" \
  --out /data/alpaca_input.jsonl

# 3) Template building the input in one shot
python hf_scrape_to_input_jsonl.py \
  --dataset databricks/databricks-dolly-15k \
  --split train \
  --template "{instruction}\n{context}\n{response}" \
  --out /data/dolly_input.jsonl \
  --min_chars 30 --dedup

# 4) Streaming a huge split
python hf_scrape_to_input_jsonl.py \
  --dataset c4 \
  --config en \
  --split train \
  --streaming \
  --out /data/c4_en_input.jsonl \
  --limit 100000
HF DATASET SCRAPER → "input"-ONLY JSONL

This script downloads a dataset from Hugging Face Datasets, extracts or builds a single "input" text field for each row, cleans it, and writes it to a .jsonl file with only the "input" key.

WHAT THIS SCRIPT DOES

Connects to Hugging Face and downloads the dataset split you choose.

Picks one or more columns from the dataset to build a single "input" string.

Optionally combines multiple columns (e.g., instruction + input → one text block).

Cleans the text (strip whitespace, remove duplicates, length filtering).

Writes each row to a .jsonl file in the form:
{"input": "your text here"}
{"input": "next row text here"}

REQUIREMENTS

Run in terminal:
pip install datasets

For private datasets:
pip install huggingface_hub
huggingface-cli login

BASIC USAGE

Save the script as hf_scrape_to_input_jsonl.py

Run:
python hf_scrape_to_input_jsonl.py --dataset <dataset_name> --split <split_name> --out <output_path.jsonl>

Example:
python hf_scrape_to_input_jsonl.py --dataset openwebtext --split train --out ./openwebtext_input.jsonl

COMMON OPTIONS

--dataset : Hugging Face dataset repo name (e.g., openwebtext, tatsu-lab/alpaca)
--split : Dataset split (e.g., train, validation, test)
--config : Config name if needed (e.g., --config en for c4 English)
--cols : Comma-separated list of columns to merge (e.g., instruction,input)
--sep : Separator for merged columns (e.g., "\n\n")
--template : Build input using Python format string (e.g., "{instruction}\n{input}\n{output}")
--min_chars : Minimum characters to keep a row (default 1)
--max_chars : Maximum characters allowed (default 200000)
--lower : Lowercase before filtering/deduplication
--dedup : Remove duplicate "input" values
--limit : Stop after N rows
--streaming : Stream dataset without downloading fully
--trust_remote_code : Allow custom dataset loader code
--out : Output JSONL file path

EXAMPLE COMMANDS

A) Simple text column dataset:
python hf_scrape_to_input_jsonl.py --dataset openwebtext --split train --out ./openwebtext_input.jsonl --limit 100000

B) Alpaca dataset (merge instruction and input):
python hf_scrape_to_input_jsonl.py --dataset tatsu-lab/alpaca --split train --cols instruction,input --sep "\n\n" --out ./alpaca_input.jsonl --dedup

C) Template formatting:
python hf_scrape_to_input_jsonl.py --dataset databricks/databricks-dolly-15k --split train --template "{instruction}\n\n{context}\n\n{response}" --out ./dolly_input.jsonl --min_chars 50

D) Streaming a massive dataset:
python hf_scrape_to_input_jsonl.py --dataset c4 --config en --split train --streaming --out ./c4_en_input.jsonl --limit 200000

OUTPUT FORMAT

Output is JSON Lines format:
{"input": "The quick brown fox jumps over the lazy dog."}
{"input": "Artificial intelligence is transforming the world."}

PRO TIPS

Use --dedup for cleaner data.

Use --streaming for large datasets to avoid full download.

To see available columns:
from datasets import load_dataset
ds = load_dataset("your_dataset", split="train")
print(ds.column_names)

Set --min_chars > 20 for better quality.
