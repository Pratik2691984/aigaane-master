from vidyut.kosha import Kosha

k = Kosha("C:/aigaane-master/data/vidyut/kosha")

# Sample the DhatuEntry list
dhatus = list(k.dhatus())
print("dhatu count:", len(dhatus))
d = dhatus[0]
print("sample dhatu type:", type(d).__name__)
print("  dhatu:", d.dhatu)
print("  artha_en:", d.artha_en)
print("  artha_sa:", d.artha_sa)
print("  pada:", d.pada)
print("  ittva:", d.ittva)
print("  karmatva:", d.karmatva)
print()

# Sample the PratipadikaEntry list
pratipadikas = list(k.pratipadikas())
print("pratipadika count:", len(pratipadikas))
p = pratipadikas[0]
print("sample pratipadika type:", type(p).__name__)
print("  lemma:", p.lemma)
print("  lingas:", p.lingas)
print("  is_avyaya:", p.is_avyaya)