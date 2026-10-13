import sys
sys.path.insert(0, ".")
from vidyut.prakriya import Vyakarana, Dhatu, Gana, Lakara, Prayoga, Purusha, Vacana, Pada

v = Vyakarana()
ganas = [
    ("Bhvadi", Gana.Bhvadi),
    ("Adadi", Gana.Adadi),
    ("Juhotyadi", Gana.Juhotyadi),
    ("Divadi", Gana.Divadi),
    ("Svadi", Gana.Svadi),
    ("Tudadi", Gana.Tudadi),
    ("Rudhadi", Gana.Rudhadi),
    ("Tanadi", Gana.Tanadi),
    ("Kryadi", Gana.Kryadi),
    ("Curadi", Gana.Curadi),
]
for label, g in ganas:
    try:
        prakriyas = v.derive(Pada.Tinanta(
            dhatu=Dhatu.mula(aupadeshika="gam", gana=g),
            prayoga=Prayoga.Kartari,
            lakara=Lakara.Lat,
            purusha=Purusha.Prathama,
            vacana=Vacana.Eka,
        ))
        print(label, "->", [p.text for p in prakriyas])
    except Exception as e:
        print(label, "-> ERROR:", type(e).__name__, str(e)[:80])