import sys
sys.path.insert(0, ".")
from vidyut.prakriya import Vyakarana, Dhatu, Gana, Lakara, Prayoga, Purusha, Vacana, Pada

v = Vyakarana()
candidates = ["gam", "gamu", "gama", "gaM", "ga", "gacCa", "gama~", "gamu~"]
for candidate in candidates:
    try:
        prakriyas = v.derive(Pada.Tinanta(
            dhatu=Dhatu.mula(aupadeshika=candidate, gana=Gana.Bhvadi),
            prayoga=Prayoga.Kartari,
            lakara=Lakara.Lat,
            purusha=Purusha.Prathama,
            vacana=Vacana.Eka,
        ))
        print(candidate, "->", [p.text for p in prakriyas])
    except Exception as e:
        print(candidate, "-> ERROR:", e)