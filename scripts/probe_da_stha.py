import sys
sys.path.insert(0, ".")
from vidyut.prakriya import Vyakarana, Dhatu, Gana, Lakara, Prayoga, Purusha, Vacana, Pada

v = Vyakarana()

candidates = {
    "dā (give)": ["dA", "dA~", "dada", "dAda", "dA3", "dAN", "dAR", "dA1"],
    "sthā (stand)": ["zwA", "sTA", "tizWa", "zwA~", "zWA", "sTA~", "tiSTha", "tizwA"],
}

for label, forms in candidates.items():
    print("==", label, "==")
    for c in forms:
        try:
            prakriyas = v.derive(Pada.Tinanta(
                dhatu=Dhatu.mula(aupadeshika=c, gana=Gana.Bhvadi),
                prayoga=Prayoga.Kartari,
                lakara=Lakara.Lat,
                purusha=Purusha.Prathama,
                vacana=Vacana.Eka,
            ))
            print("  %-10s -> %s" % (c, [p.text for p in prakriyas]))
        except Exception as e:
            print("  %-10s -> ERROR: %s" % (c, str(e)[:60]))