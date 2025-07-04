import json
import glob

files = glob.glob("data/divisions-administratives-v2r1-20250101/*.json")

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
