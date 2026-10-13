from vidyut.kosha import Kosha, PadaEntry, DhatuEntry, PratipadikaEntry

print("Kosha methods:", [n for n in dir(Kosha) if not n.startswith("_")])
print()
print("Kosha doc:", (Kosha.__doc__ or "").strip())
print()
for name in [n for n in dir(Kosha) if not n.startswith("_")]:
    obj = getattr(Kosha, name)
    print(f"--- {name} ---")
    print("  type:", type(obj).__name__)
    doc = (getattr(obj, "__doc__", "") or "").strip()
    if doc:
        for line in doc.splitlines()[:6]:
            print("   ", line)
    print()

print("PadaEntry methods:", [n for n in dir(PadaEntry) if not n.startswith("_")])
print()
for name in [n for n in dir(PadaEntry) if not n.startswith("_")]:
    obj = getattr(PadaEntry, name)
    print(f"--- PadaEntry.{name} ---")
    print("  type:", type(obj).__name__)
    doc = (getattr(obj, "__doc__", "") or "").strip()
    if doc:
        for line in doc.splitlines()[:4]:
            print("   ", line)

print()
print("DhatuEntry methods:", [n for n in dir(DhatuEntry) if not n.startswith("_")])
print("PratipadikaEntry methods:", [n for n in dir(PratipadikaEntry) if not n.startswith("_")])