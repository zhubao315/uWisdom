#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
EXPORT = ROOT / "data" / "export"

def main():
    index_file = ASSETS / "search-index.json"
    if not index_file.exists():
        print("Error: search-index.json not found. Run build_site_data.py first.")
        return

    data = json.loads(index_file.read_text(encoding="utf-8"))
    entries = data["entries"]
    
    EXPORT.mkdir(parents=True, exist_ok=True)
    
    # Export full JSON
    (EXPORT / "uwisdom_full.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Export as simple list for other tools
    simple = [{"title": e["title"], "url": e["url"], "tags": e["tags"]} for e in entries]
    (EXPORT / "uwisdom_list.json").write_text(json.dumps(simple, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"Exported {len(entries)} entries to {EXPORT}")

if __name__ == "__main__":
    main()
