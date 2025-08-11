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


HF Dataset Scraper → input-only JSONL
This script downloads a dataset from Hugging Face Datasets, extracts or builds a single "input" text field for each row, cleans it, and writes it to a .jsonl file (JSON Lines format) with only the "input" key.

1. What this script does
Connects to Hugging Face and downloads the dataset split you choose.

Picks one or more columns from the dataset to build a single "input" string.

Optionally combines multiple columns (e.g., instruction + input → one text block).

Cleans the text (strip whitespace, remove duplicates, length filtering).

Writes each row to a .jsonl file:

json
Copy
Edit
{"input": "your text here"}
{"input": "next row text here"}
Nothing else. No labels, no metadata, just "input".

2. What you need installed
Run these in your terminal:

bash
Copy
Edit
pip install datasets
If you want to download private datasets, also run:

bash
Copy
Edit
pip install huggingface_hub
huggingface-cli login
3. Script usage
Save the Python script from above as hf_scrape_to_input_jsonl.py.

Run it like this:

bash
Copy
Edit
python hf_scrape_to_input_jsonl.py \
  --dataset <dataset_name> \
  --split <split_name> \
  --out <output_path.jsonl>
Basic example:

bash
Copy
Edit
python hf_scrape_to_input_jsonl.py \
  --dataset openwebtext \
  --split train \
  --out ./openwebtext_input.jsonl
4. Common options explained
Option	What it does	Example
--dataset	The Hugging Face dataset repo name.	openwebtext, tatsu-lab/alpaca
--split	Which split to use.	train, validation, test
--config	If the dataset has multiple configs.	--config en for C4 English
--cols	Comma-separated list of text columns to merge.	--cols instruction,input
--sep	Separator when joining columns.	--sep "\n\n"
--template	Build the "input" using a Python format string.	--template "{instruction}\n{input}\n{output}"
--min_chars	Skip rows shorter than this many characters.	--min_chars 30
--max_chars	Skip rows longer than this many characters.	--max_chars 2000
--lower	Lowercase text before filtering/deduplication.	--lower
--dedup	Remove duplicate "input" values.	--dedup
--limit	Stop after this many rows.	--limit 50000
--streaming	Stream the dataset without full download (for huge datasets).	--streaming
--trust_remote_code	Needed if the dataset loader has custom Python code.	--trust_remote_code
--out	Output .jsonl file path.	--out ./data.jsonl

5. Example scenarios
A) Simple "text" column dataset

bash
Copy
Edit
python hf_scrape_to_input_jsonl.py \
  --dataset openwebtext \
  --split train \
  --out ./openwebtext_input.jsonl \
  --limit 100000
B) Alpaca dataset (merge instruction and input)

bash
Copy
Edit
python hf_scrape_to_input_jsonl.py \
  --dataset tatsu-lab/alpaca \
  --split train \
  --cols instruction,input \
  --sep "\n\n" \
  --out ./alpaca_input.jsonl \
  --dedup
C) Template formatting

bash
Copy
Edit
python hf_scrape_to_input_jsonl.py \
  --dataset databricks/databricks-dolly-15k \
  --split train \
  --template "{instruction}\n\n{context}\n\n{response}" \
  --out ./dolly_input.jsonl \
  --min_chars 50
D) Streaming a massive dataset

bash
Copy
Edit
python hf_scrape_to_input_jsonl.py \
  --dataset c4 \
  --config en \
  --split train \
  --streaming \
  --out ./c4_en_input.jsonl \
  --limit 200000
6. Output format
The output file is in JSON Lines format, which means:

One JSON object per line.

Each object has exactly one key: "input".

Example:

json
Copy
Edit
{"input": "The quick brown fox jumps over the lazy dog."}
{"input": "Artificial intelligence is transforming the world."}
7. Pro tips
Use --dedup for cleaner data.

Use --streaming for large datasets like c4 to avoid full download.

If unsure which columns are available, run:

python
Copy
Edit
from datasets import load_dataset
ds = load_dataset("your_dataset", split="train")
print(ds.column_names)
Keep --min_chars > 20 for better quality text.
