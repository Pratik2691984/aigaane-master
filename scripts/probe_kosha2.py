from pathlib import Path
from vidyut.kosha import Kosha

kosha_dir = Path("C:/aigaane-master/data/vidyut/kosha")
print("kosha dir:", kosha_dir)
print("files:", [p.name for p in kosha_dir.iterdir()])

# Try to construct from the directory
try:
    k = Kosha(str(kosha_dir))
    print("Kosha(dir) ok:", type(k).__name__)
except Exception as e:
    print("Kosha(dir) failed:", type(e).__name__, e)

# Try to construct from a file
try:
    k = Kosha(str(kosha_dir / "registry.msgpack"))
    print("Kosha(file) ok:", type(k).__name__)
except Exception as e:
    print("Kosha(file) failed:", type(e).__name__, e)