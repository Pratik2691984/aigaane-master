from pathlib import Path
from vidyut.sandhi import Splitter

data = Path("C:/aigaane-master/data/vidyut")
sandhi_dir = data / "sandhi"

print("sandhi data dir contents:")
for p in sorted(sandhi_dir.rglob("*")):
    if p.is_file():
        print("  ", p.relative_to(data), p.stat().st_size, "bytes")

csv_candidates = list(sandhi_dir.rglob("*.csv"))
print()
print("csv candidates:", [str(p) for p in csv_candidates])

if not csv_candidates:
    raise SystemExit("no .csv found in sandhi data")

s = Splitter.from_csv(str(csv_candidates[0]))
print("constructor ok:", type(s).__name__)

text = "rAmaSca"
for idx in (3, 4, 5):
    try:
        result = s.split_at(text, idx)
        print(f"split_at({text!r}, {idx}): {result}")
        if isinstance(result, list):
            for r in result:
                print("   first=", r.first, "second=", r.second, "valid=", r.is_valid)
        else:
            print("   first=", result.first, "second=", result.second, "valid=", result.is_valid)
    except Exception as e:
        print(f"split_at({text!r}, {idx}): ERROR", type(e).__name__, e)