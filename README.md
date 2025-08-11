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
