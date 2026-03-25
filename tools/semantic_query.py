#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI

ROOT = Path("/root/uWisdom")
DATA = ROOT / "data" / "semantic"


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 tools/semantic_query.py "你的问题"')
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required")

    query = sys.argv[1]
    metadata = json.loads((DATA / "metadata.json").read_text(encoding="utf-8"))
    index = faiss.read_index(str(DATA / "knowledge.faiss"))

    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
        encoding_format="float",
    )
    vector = np.array([response.data[0].embedding], dtype="float32")
    faiss.normalize_L2(vector)

    scores, indices = index.search(vector, 5)
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        item = metadata[idx]
        print(f"{rank}. {item['title']} | {item['url']} | score={score:.4f}")
        print(f"   {item.get('summary', '')}")


if __name__ == "__main__":
    main()

