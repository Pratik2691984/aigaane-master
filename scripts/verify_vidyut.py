from vidyut.prakriya import Vyakarana, Dhatu, Gana, Lakara, Prayoga, Purusha, Vacana, Pada

v = Vyakarana()

prakriyas = v.derive(Pada.Tinanta(
    dhatu=Dhatu.mula(aupadeshika="BU", gana=Gana.Bhvadi),
    prayoga=Prayoga.Kartari,
    lakara=Lakara.Lat,
    purusha=Purusha.Prathama,
    vacana=Vacana.Eka,
))

print("count:", len(prakriyas))
for i, p in enumerate(prakriyas):
    print(i, "text:", p.text)
    print(i, "history len:", len(p.history))
    if p.history:
        first = p.history[0]
        print(i, "first step type:", type(first).__name__)
        print(i, "first step attrs:", [a for a in dir(first) if not a.startswith("_")])