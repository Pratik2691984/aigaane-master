import pytest
from aigaane.tala import align_to_tala
from aigaane.raga import RAGAS, assign_svaras, svara_ratio

def test_ratio_panchama():
    assert svara_ratio("mayamalavagowla", "P") == 1.5
def test_ratio_gandhara():
    assert abs(svara_ratio("mayamalavagowla", "G3") - 1.25) < 1e-9
def test_ratio_unknown_raises():
    with pytest.raises(KeyError):
        svara_ratio("mayamalavagowla", "M2")
def test_assign_length():
    aligned = align_to_tala(list("GGGGLGGG"), "adi")
    assert len(assign_svaras(aligned, "mayamalavagowla")) == 8
def test_assign_pada_boundary():
    aligned = align_to_tala(list("GGGGLGGG" + "LLGGLGLG"), "adi")
    svaras = assign_svaras(aligned, "mayamalavagowla")
    assert svaras[0]["svara"] == "S"
    assert svaras[8]["svara"] == "S"
def test_negative_input():
    a = assign_svaras(align_to_tala(list("GGGG"), "adi"), "mayamalavagowla")
    b = assign_svaras(align_to_tala(list("LL"), "adi"), "mayamalavagowla")
    assert [c["svara"] for c in a] != [c["svara"] for c in b]
