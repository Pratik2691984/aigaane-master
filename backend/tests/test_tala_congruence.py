"""
Regression tests for v2.0 tala congruence.
"""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.engine import _tala


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ------------------------------------------------------------------ #
#   Pure-function tests                                              #
# ------------------------------------------------------------------ #

class TestCheckCongruence:
    def test_strict_formula_documented_example(self):
        # 3*5 + 2*1 + 0 = 17, congruent mod 8
        r = _tala.check_congruence(pluta_count=5, dirgha_count=1, cycle_length=8)
        assert r.congruent is True
        assert r.total_matras == 17
        assert r.residue == 1
        assert r.target == 17 % 8

    def test_laghu_zero_matches_strict_formula(self):
        r = _tala.check_congruence(3, 4, 8, t_start=0, laghu_count=0)
        assert r.total_matras == 17
        assert r.congruent is True

    def test_laghu_extension_changes_result(self):
        base = _tala.check_congruence(2, 2, 8, laghu_count=0)
        ext = _tala.check_congruence(2, 2, 8, laghu_count=1)
        assert ext.total_matras == base.total_matras + 1
        assert (ext.residue - base.residue) % 8 == 1

    def test_not_congruent_reports_deviation(self):
        # P=1, D=0 -> total=3. Nearest congruent total is 1 (= 17 - 2*8),
        # so signed distance from that nearest landing is 3 - 1 = +2.
        r = _tala.check_congruence(1, 0, 8)
        assert r.congruent is False
        assert r.total_matras == 3
        assert r.deviation == 2

    def test_sam_landing(self):
        r = _tala.check_congruence(5, 1, 8)
        assert r.sam_landing == 17 % 8

    def test_rejects_negative_inputs(self):
        with pytest.raises(ValueError):
            _tala.check_congruence(-1, 0, 8)
        with pytest.raises(ValueError):
            _tala.check_congruence(0, 0, 0)

    def test_custom_anchor(self):
        r = _tala.check_congruence(0, 1, 5, sam_anchor=2)
        assert r.congruent is True


class TestTalaRegistry:
    def test_registry_has_adi_8(self):
        spec = _tala.lookup_tala("adi")
        assert spec is not None
        assert spec.cycle_length == 8

    def test_case_insensitive(self):
        assert _tala.lookup_tala("ADI").cycle_length == 8
        assert _tala.lookup_tala("Adi").cycle_length == 8

    def test_unknown_returns_none(self):
        assert _tala.lookup_tala("nonexistent_tala") is None

    def test_list_talas_returns_all(self):
        talas = _tala.list_talas()
        assert len(talas) == len(_tala.TALA_REGISTRY)


class TestSuggestCorrection:
    def test_already_congruent(self):
        s = _tala.suggest_correction(5, 1, 8)
        assert s["already_congruent"] is True

    def test_suggests_alternative_cycles(self):
        s = _tala.suggest_correction(1, 0, 8)
        assert s["already_congruent"] is False
        assert "corrections" in s
        assert "shift_t_start" in s["corrections"]


# ------------------------------------------------------------------ #
#   HTTP endpoint tests                                              #
# ------------------------------------------------------------------ #

def test_tala_list_endpoint(client):
    r = client.get("/api/v3/studio3/tala/list")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 10


def test_tala_lookup_found(client):
    r = client.get("/api/v3/studio3/tala/lookup", params={"name": "adi"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is True
    assert data["spec"]["cycle_length"] == 8


def test_tala_lookup_not_found(client):
    r = client.get("/api/v3/studio3/tala/lookup", params={"name": "xyz"})
    assert r.status_code == 200
    assert r.json()["found"] is False


def test_congruence_endpoint_congruent(client):
    r = client.post(
        "/api/v3/studio3/tala/congruence",
        json={"pluta_count": 5, "dirgha_count": 1, "cycle_length": 8},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["congruent"] is True
    assert data["total_matras"] == 17


def test_congruence_endpoint_not_congruent(client):
    r = client.post(
        "/api/v3/studio3/tala/congruence",
        json={"pluta_count": 1, "dirgha_count": 0, "cycle_length": 8},
    )
    assert r.status_code == 200
    assert r.json()["congruent"] is False


def test_congruence_by_tala_name(client):
    r = client.post(
        "/api/v3/studio3/tala/congruence/by-tala",
        json={"pluta_count": 5, "dirgha_count": 1, "tala_name": "adi"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["tala"]["cycle_length"] == 8
    assert data["result"]["congruent"] is True


def test_congruence_by_unknown_tala_404(client):
    r = client.post(
        "/api/v3/studio3/tala/congruence/by-tala",
        json={"pluta_count": 1, "dirgha_count": 0, "tala_name": "bogus"},
    )
    assert r.status_code == 404


def test_congruence_rejects_negative_via_422(client):
    r = client.post(
        "/api/v3/studio3/tala/congruence",
        json={"pluta_count": -1, "dirgha_count": 0, "cycle_length": 8},
    )
    assert r.status_code == 422


def test_suggest_endpoint(client):
    r = client.post(
        "/api/v3/studio3/tala/suggest",
        json={"pluta_count": 1, "dirgha_count": 0, "cycle_length": 8},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["already_congruent"] is False
    assert "corrections" in data


def test_probe_reports_tala_implemented(client):
    r = client.get("/api/v3/studio3/probe")
    assert r.status_code == 200
    data = r.json()
    assert data["tala_ok"] is True
    assert data["tala_congruence"] == "implemented (v2.0)"
    assert data["has_check_congruence"] is True