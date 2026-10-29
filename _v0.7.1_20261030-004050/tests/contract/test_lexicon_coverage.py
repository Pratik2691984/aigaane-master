import pytest
import _lexicon

def test_no_borrowed_future_stem_collisions():
    """Aster bhūḥ (2.4.52): Defective roots like 'as' must not steal stem_fut from 'bhū'."""
    stems = {}
    for dhatu, info in _lexicon._DHATUPATHA.items():
        fut = info.get("stem_fut")
        if fut:
            assert fut not in stems, (
                f"Duplicate stem_fut '{fut}' found in dhātu '{dhatu}'; already mapped to '{stems[fut]}'"
            )
            stems[fut] = dhatu

def test_bhavisyati_resolves_strictly_to_bhu():
    res = _lexicon.lookup("bhaviṣyati")
    assert res is not None
    assert res["dhatu"] == "bhū", f"bhaviṣyati must resolve to 'bhū', got '{res.get('dhatu')}'"

def test_every_root_has_verified_resolution():
    """Verify that every root in _DHATUPATHA has at least one working inflected form."""
    root_sample_forms = {
        "bhū": "bhavati",
        "gam": "gacchati",
        "paṭh": "paṭhati",
        "kṛ": "karoti",
        "pā": "pibati",
        "labh": "labhate",
        "dā": "dadāti",
        "viś": "viśati",
        "vah": "vahati",
        "likh": "likhati",
        "vad": "vadati",
        "cur": "corayati",
        "hu": "juhoti",
        "as": "asti",
        "jñā": "jānāti",
    }
    
    for dhatu, info in _lexicon._DHATUPATHA.items():
        assert dhatu in root_sample_forms, f"Dhātu '{dhatu}' lacks a registered sample form in test suite."
        sample = root_sample_forms[dhatu]
        res = _lexicon.lookup(sample)
        assert res is not None, f"Sample form '{sample}' for dhātu '{dhatu}' returned None."
        assert res["dhatu"] == dhatu, f"Sample form '{sample}' mapped to '{res['dhatu']}', expected '{dhatu}'."

def test_untested_ganas_lit_forms():
    """Verify Liṭ forms for additional Gaṇa entries where stem_perf is defined."""
    # dā -> dadau (Gaṇa 3)
    res_da = _lexicon.lookup("dadau")
    assert res_da is not None
    assert res_da["dhatu"] == "dā"
    assert res_da["vacana"] == "ekavacana"

    # viś -> viveśa (Gaṇa 6)
    res_vis = _lexicon.lookup("viveśa")
    assert res_vis is not None
    assert res_vis["dhatu"] == "viś"
    assert res_vis["vacana"] == "ekavacana"
