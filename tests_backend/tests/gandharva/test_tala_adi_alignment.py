import pytest
from aigaane.tala import TALAS, align_to_tala

def test_adi_grid_shape():
    assert TALAS["adi"]["aksharas"] == 8
    assert TALAS["adi"]["vibhagas"] == [4, 2, 2]
def test_single_pada_fits_one_cycle():
    aligned = align_to_tala(list("GGGGLGGG"), "adi")
    assert len(aligned) == 8
    assert [c["akshara"] for c in aligned] == [1,2,3,4,5,6,7,8]
def test_vibhaga_boundaries():
    aligned = align_to_tala(list("GGGGLGGG"), "adi")
    assert [c["vibhaga"] for c in aligned] == [0,0,0,0,1,1,2,2]
def test_two_padas_wrap():
    aligned = align_to_tala(list("GGGGLGGG" + "LLGGLGLG"), "adi")
    assert len(aligned) == 16
    assert [c["cycle"] for c in aligned[8:]] == [1]*8
def test_negative_wrong_length():
    assert len(align_to_tala(list("GGGLL"), "adi")) == 5
def test_unknown_tala_raises():
    with pytest.raises(KeyError):
        align_to_tala(list("GGGGLGGG"), "nonexistent")
