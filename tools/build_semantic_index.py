#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI

ROOT = Path("/root/uWisdom")
ASSETS = ROOT / "docs" / "assets"
OUTPUT = ROOT / "data" / "semantic"


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required")

    entries = json.loads((ASSETS / "search-index.json").read_text(encoding="utf-8"))["entries"]
    texts = []
    metadata = []
    for entry in entries:
        text = "\n".join(
            [
                entry["title"],
                entry.get("summary", ""),
                entry.get("domain", ""),
                " ".join(entry.get("tags", [])),
                entry.get("content", ""),
            ]
        )
        texts.append(text)
        metadata.append({k: entry[k] for k in ("url", "title", "summary", "section", "domain", "tags", "version", "author", "book")})

    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
        encoding_format="float",
    )
    matrix = np.array([item.embedding for item in response.data], dtype="float32")
    faiss.normalize_L2(matrix)

    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(OUTPUT / "knowledge.faiss"))
    (OUTPUT / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / "manifest.json").write_text(
        json.dumps(
            {
                "model": "text-embedding-3-small",
                "count": len(metadata),
                "dimensions": int(matrix.shape[1]),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"built semantic index with {len(metadata)} entries")


if __name__ == "__main__":
    main()

