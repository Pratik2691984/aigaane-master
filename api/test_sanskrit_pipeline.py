import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kernel_api import app
from engines.vyakarana import (
    LEXICAL_SOURCE_GOVERNANCE,
    analyze_sanskrit,
    final_form_cleanup,
)


ROOT = Path(__file__).resolve().parents[1]


class SanskritPipelineTests(unittest.TestCase):
    def test_cosmic_angle_removed_from_shell_dom(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        removed_terms = [
            "Cosmic " + "Angle",
            "COSMIC " + "ANGLE",
            "cosmic-" + "angle",
            "main-" + "slider",
            "angle-" + "readout",
            "slider" + "Moved",
        ]
        for term in removed_terms:
            self.assertNotIn(term, html)

    def test_no_cosmic_angle_js_reference_remains(self):
        js_files = [
            ROOT / "ui" / "tabs" / "sanskrit" / "controller.js",
            ROOT / "tools" / "sanskrit.tool.js",
        ]
        for path in js_files:
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("cosmic" + "Angle", source)
            self.assertNotIn("angle" + "Slider", source)
            self.assertNotIn("main-" + "slider", source)
            self.assertNotIn("slider" + "Moved", source)

    def test_sanskrit_tab_has_no_symbolic_coupling_terms(self):
        for path in [
            ROOT / "ui" / "tabs" / "sanskrit" / "view.html",
            ROOT / "ui" / "tabs" / "sanskrit" / "controller.js",
            ROOT / "ui" / "tabs" / "sanskrit" / "style.css",
            ROOT / "tools" / "sanskrit.tool.js",
        ]:
            source = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("nakshatra", source)
            self.assertNotIn("49d", source)
            self.assertNotIn("cosmic", source)

    def test_analyze_response_renders_required_contract_fields(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/analyze",
            json={"input_text": "agnim ile purohitam yajnasya devam rtvijam"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("overall_stanza_meter", payload)
        self.assertGreater(payload["total_matra_count"], 0)
        self.assertTrue(payload["padas"])
        self.assertTrue(payload["phonological_syllables"])
        self.assertTrue(payload["derivation_history"])
        self.assertIn("experimental_payload", payload)
        self.assertEqual(
            payload["experimental_payload"]["label"],
            "Experimental Symbolic Structural Projection Field Map",
        )

    def test_post_analyze_route_is_registered_and_get_does_not_replace_it(self):
        client = TestClient(app)
        post_response = client.post("/api/v3/analyze", json={"input_text": "ramah avadat"})
        self.assertEqual(post_response.status_code, 200)
        self.assertTrue(post_response.json()["padas"])

        get_response = client.get("/api/v3/analyze")
        self.assertIn(get_response.status_code, {404, 405})

        options_response = client.options(
            "/api/v3/analyze",
            headers={
                "Origin": "http://localhost:5500",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        self.assertIn(options_response.status_code, {200, 204})
        self.assertIn("POST", options_response.headers.get("access-control-allow-methods", "POST"))

    def test_frontend_still_posts_json_to_analyze_endpoint(self):
        controller = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn('fetch("/api/v3/analyze"', controller)
        self.assertIn('method: "POST"', controller)
        self.assertIn('"Content-Type": "application/json"', controller)
        self.assertIn("JSON.stringify", controller)

    def test_devanagari_and_iast_ingress_are_safe(self):
        devanagari = analyze_sanskrit("\u0930\u093e\u092e\u0903 \u0905\u0935\u0926\u0924\u094d")
        iast = analyze_sanskrit("r\u0101ma\u1e25 avadat")
        self.assertEqual(devanagari["transliteration"], "ramah avadat")
        self.assertEqual(iast["transliteration"], "ramah avadat")
        self.assertTrue(devanagari["padas"])
        self.assertTrue(iast["phonological_syllables"])

    def test_chandas_segments_ramah_avadat_exactly(self):
        expected_syllables = ["\u0930\u093e", "\u092e\u0903", "\u0905", "\u0935", "\u0926\u0924\u094d"]
        expected_weights = ["Guru", "Guru", "Laghu", "Laghu", "Guru"]
        expected_matras = [2, 2, 1, 1, 2]

        payload = analyze_sanskrit("\u0930\u093e\u092e\u0903 \u0905\u0935\u0926\u0924\u094d")
        syllables = payload["phonological_syllables"]
        self.assertEqual([node["text"] for node in syllables], expected_syllables)
        self.assertEqual([node["weight"] for node in syllables], expected_weights)
        self.assertEqual([node["matra_count"] for node in syllables], expected_matras)
        self.assertEqual(payload["total_matra_count"], 8)
        self.assertEqual(payload["padas"][0]["guru_laghu_pattern"], "G G L L G")
        self.assertIn("Fragment", payload["overall_stanza_meter"])

    def test_iast_ramah_avadat_preserves_latin_display(self):
        payload = analyze_sanskrit("r\u0101ma\u1e25 avadat")
        syllables = payload["phonological_syllables"]
        self.assertEqual([node["text"] for node in syllables], ["r\u0101", "ma\u1e25", "a", "va", "dat"])
        self.assertEqual([node["weight"] for node in syllables], ["Guru", "Guru", "Laghu", "Laghu", "Guru"])
        self.assertEqual([node["matra_count"] for node in syllables], [2, 2, 1, 1, 2])

    def test_latin_purohitam_syllabifies_by_onset_rule(self):
        payload = analyze_sanskrit("purohitam")
        syllables = payload["phonological_syllables"]
        self.assertEqual([node["text"] for node in syllables], ["pu", "ro", "hi", "tam"])
        self.assertEqual([node["weight"] for node in syllables], ["Laghu", "Guru", "Laghu", "Guru"])
        self.assertEqual([node["matra_count"] for node in syllables], [1, 2, 1, 2])
        self.assertEqual(payload["total_matra_count"], 6)

    def test_latin_devam_rtvijam_keeps_final_codas(self):
        payload = analyze_sanskrit("devam rtvijam")
        syllables = payload["phonological_syllables"]
        texts = [node["text"] for node in syllables]
        weights = {node["text"]: node["weight"] for node in syllables}
        self.assertNotIn("am", texts)
        self.assertIn("vam", texts)
        self.assertEqual(weights["vam"], "Guru")
        self.assertIn("jam", texts)
        self.assertEqual(weights["jam"], "Guru")
        diagnostics = " ".join(item["message"] for item in payload["parser_diagnostics"])
        self.assertNotIn("failed", diagnostics.lower())

    def test_latin_rtvijam_vocalic_r(self):
        payload = analyze_sanskrit("devam rtvijam")
        syllables = payload["phonological_syllables"]
        self.assertEqual([node["text"] for node in syllables], ["de", "vam", "\u1e5b", "tvi", "jam"])
        self.assertEqual([node["weight"] for node in syllables], ["Guru", "Guru", "Guru", "Laghu", "Guru"])
        self.assertEqual([node["matra_count"] for node in syllables], [2, 2, 2, 1, 2])
        self.assertEqual(payload["total_matra_count"], 9)

    def test_iast_rtvijam_vocalic_r(self):
        payload = analyze_sanskrit("devam \u1e5btvijam")
        self.assertEqual([node["text"] for node in payload["phonological_syllables"]], ["de", "vam", "\u1e5b", "tvi", "jam"])

    def test_latin_script_display_consistency(self):
        payload = analyze_sanskrit("somah vayuh")
        texts = [node["text"] for node in payload["phonological_syllables"]]
        self.assertNotIn("\u0935", texts)
        self.assertEqual(texts, ["so", "mah", "va", "yuh"])

    def test_iast_agnimile_merges_l_vowel_edge(self):
        payload = analyze_sanskrit("agnim\u012b\u1e37e purohitam")
        syllables = payload["phonological_syllables"]
        self.assertEqual([node["text"] for node in syllables], ["ag", "ni", "m\u012b", "\u1e37e", "pu", "ro", "hi", "tam"])
        self.assertEqual([node["weight"] for node in syllables], ["Guru", "Laghu", "Guru", "Guru", "Laghu", "Guru", "Laghu", "Guru"])
        self.assertEqual(len(syllables), 8)
        self.assertEqual(payload["padas"][0]["syllable_count"], 8)

    def test_single_all_guru_pada_is_vidyunmala_candidate(self):
        payload = analyze_sanskrit("\u0938\u094b\u092e\u0903 \u092a\u0942\u0937\u093e \u0926\u0947\u0935\u094b \u0935\u093e\u092f\u0941\u0903")
        self.assertEqual(payload["padas"][0]["syllable_count"], 8)
        self.assertEqual(payload["padas"][0]["guru_laghu_pattern"], "G G G G G G G G")
        self.assertEqual(payload["overall_stanza_meter"], "Vidyunm\u0101l\u0101 p\u0101da candidate")

    def test_gayatri_fragment_stays_partial_pada(self):
        payload = analyze_sanskrit("G\u0101yatr\u012b")
        self.assertEqual(len(payload["phonological_syllables"]), 3)
        self.assertIn("Fragment / partial pada", payload["overall_stanza_meter"])

    def test_latin_phrase_does_not_detach_purohitam_codas(self):
        payload = analyze_sanskrit("agnim ile purohitam")
        texts = [node["text"] for node in payload["phonological_syllables"]]
        for bad in ["pur", "oh", "it", "am"]:
            self.assertNotIn(bad, texts)
        for expected in ["pu", "ro", "hi", "tam"]:
            self.assertIn(expected, texts)

    def test_latin_pipe_input_processes_each_pada_without_detached_am(self):
        payload = analyze_sanskrit(
            "agnim ile purohitam | yajnasya devam rtvijam | hotaram ratnadhatamam ||"
        )
        self.assertEqual(len(payload["pada_segments"]), 3)
        self.assertEqual(len(payload["padas"]), 3)
        texts = [node["text"] for node in payload["phonological_syllables"]]
        self.assertNotIn("am", texts)
        for node in payload["phonological_syllables"]:
            if node["text"].endswith("m"):
                self.assertEqual(node["weight"], "Guru")

    def test_latin_gayatri_pipe_structure(self):
        payload = analyze_sanskrit(
            "agnim ile purohitam | yajnasya devam rtvijam | hotaram ratnadhatamam ||"
        )
        self.assertEqual(len(payload["padas"]), 3)
        self.assertEqual(payload["padas"][1]["syllable_count"], 8)
        self.assertNotIn("am", [node["text"] for node in payload["phonological_syllables"]])

    def test_gayatri_structural_candidate(self):
        payload = analyze_sanskrit(
            "agnim ile purohitam | yajnasya devam rtvijam | hotaram ratnadhatamam ||"
        )
        self.assertEqual(len(payload["padas"]), 3)
        self.assertEqual([pada["syllable_count"] for pada in payload["padas"]], [8, 8, 8])
        self.assertEqual(payload["overall_stanza_meter"], "G\u0101yatr\u012b \u2014 24-syllable Vedic matrix")

    def test_undelimited_gayatri_words_do_not_force_gayatri(self):
        payload = analyze_sanskrit(
            "agnim ile purohitam yajnasya devam rtvijam hotaram ratnadhatamam"
        )
        self.assertNotEqual(payload["overall_stanza_meter"], "G\u0101yatr\u012b \u2014 24-syllable Vedic matrix")

    def test_vocalic_r_conjunct_promotion(self):
        payload = analyze_sanskrit("devam rtvijam")
        syllables = payload["phonological_syllables"]
        self.assertEqual([node["text"] for node in syllables], ["de", "vam", "\u1e5b", "tvi", "jam"])
        self.assertEqual([node["weight"] for node in syllables], ["Guru", "Guru", "Guru", "Laghu", "Guru"])
        self.assertEqual(payload["total_matra_count"], 9)

    def test_no_ascii_long_vowel_guessing(self):
        payload = analyze_sanskrit("hotaram ratnadhatamam")
        texts = [node["text"] for node in payload["phonological_syllables"]]
        self.assertIn("ta", texts)
        self.assertIn("dha", texts)
        self.assertNotIn("t\u0101", texts)
        self.assertNotIn("dh\u0101", texts)

    def test_explicit_iast_long_vowels(self):
        payload = analyze_sanskrit("hot\u0101ram ratnadh\u0101tamam")
        weights = {node["text"]: node["weight"] for node in payload["phonological_syllables"]}
        self.assertEqual(weights["t\u0101"], "Guru")
        self.assertEqual(weights["dh\u0101"], "Guru")

    def test_danda_split_preserves_pada_segments_and_avagraha(self):
        payload = analyze_sanskrit(
            "\u0938\u094b\u092e\u0903 \u092a\u0942\u0937\u093e \u0926\u0947\u0935\u094b \u0935\u093e\u092f\u0941\u0903 "
            "\u0964 "
            "\u0938\u0942\u0930\u094d\u092f\u094b \u092e\u093f\u0924\u094d\u0930\u094b \u0935\u0930\u0941\u0923\u094b\u093d\u0917\u094d\u0928\u093f\u0903 "
            "\u0965"
        )
        self.assertEqual(len(payload["padas"]), 2)
        self.assertEqual(len(payload["pada_segments"]), 2)
        self.assertEqual(
            [segment["text"] for segment in payload["pada_segments"]],
            [
                "\u0938\u094b\u092e\u0903 \u092a\u0942\u0937\u093e \u0926\u0947\u0935\u094b \u0935\u093e\u092f\u0941\u0903",
                "\u0938\u0942\u0930\u094d\u092f\u094b \u092e\u093f\u0924\u094d\u0930\u094b \u0935\u0930\u0941\u0923\u094b\u093d\u0917\u094d\u0928\u093f\u0903",
            ],
        )
        self.assertIn("Partial", payload["overall_stanza_meter"])
        diagnostics = " ".join(item["message"] for item in payload["parser_diagnostics"])
        self.assertNotIn("U+093D", diagnostics)

    def test_ascii_pipe_half_verse_splits_to_four_anustubh_padas(self):
        payload = analyze_sanskrit(
            "dharmaksetre kuruksetre samaveta yuyutsavah | "
            "mamakah pandavascaiva kimakurvata sanjaya ||"
        )
        self.assertEqual(len(payload["pada_segments"]), 2)
        self.assertEqual(len(payload["padas"]), 4)
        self.assertEqual([pada["syllable_count"] for pada in payload["padas"]], [8, 8, 8, 8])
        self.assertEqual(payload["overall_stanza_meter"], "Anu\u1e63\u1e6dubh / \u015aloka \u2014 32-syllable matrix")

    def test_anustubh_half_verse_expansion(self):
        first_half = (
            "\u0927\u0930\u094d\u092e\u0915\u094d\u0937\u0947\u0924\u094d\u0930\u0947 "
            "\u0915\u0941\u0930\u0941\u0915\u094d\u0937\u0947\u0924\u094d\u0930\u0947 "
            "\u0938\u092e\u0935\u0947\u0924\u093e \u092f\u0941\u092f\u0941\u0924\u094d\u0938\u0935\u0903"
        )
        second_half = (
            "\u092e\u093e\u092e\u0915\u093e\u0903 "
            "\u092a\u093e\u0923\u094d\u0921\u0935\u093e\u0936\u094d\u091a\u0948\u0935 "
            "\u0915\u093f\u092e\u0915\u0941\u0930\u094d\u0935\u0924 \u0938\u091e\u094d\u091c\u092f"
        )
        payload = analyze_sanskrit(f"{first_half} | {second_half} ||")
        self.assertEqual(len(payload["padas"]), 4)
        self.assertEqual([pada["syllable_count"] for pada in payload["padas"]], [8, 8, 8, 8])
        self.assertNotEqual(payload["padas"][0]["text"], payload["padas"][1]["text"])
        self.assertNotEqual(payload["padas"][2]["text"], payload["padas"][3]["text"])
        self.assertEqual(payload["overall_stanza_meter"], "Anu\u1e63\u1e6dubh / \u015aloka \u2014 32-syllable matrix")

    def test_no_duplicate_half_verse_display(self):
        first_half = (
            "\u0927\u0930\u094d\u092e\u0915\u094d\u0937\u0947\u0924\u094d\u0930\u0947 "
            "\u0915\u0941\u0930\u0941\u0915\u094d\u0937\u0947\u0924\u094d\u0930\u0947 "
            "\u0938\u092e\u0935\u0947\u0924\u093e \u092f\u0941\u092f\u0941\u0924\u094d\u0938\u0935\u0903"
        )
        second_half = (
            "\u092e\u093e\u092e\u0915\u093e\u0903 "
            "\u092a\u093e\u0923\u094d\u0921\u0935\u093e\u0936\u094d\u091a\u0948\u0935 "
            "\u0915\u093f\u092e\u0915\u0941\u0930\u094d\u0935\u0924 \u0938\u091e\u094d\u091c\u092f"
        )
        payload = analyze_sanskrit(f"{first_half} | {second_half} ||")
        for pada in payload["padas"]:
            self.assertNotEqual(pada["text"], first_half)
            self.assertNotEqual(pada["text"], second_half)
            self.assertEqual(len(pada["phonological_syllables"]), 8)

    def test_devanagari_gayatri_still_works(self):
        payload = analyze_sanskrit(
            "\u0905\u0917\u094d\u0928\u093f\u092e\u0940\u0933\u0947 \u092a\u0941\u0930\u094b\u0939\u093f\u0924\u0902 | "
            "\u092f\u091c\u094d\u091e\u0938\u094d\u092f \u0926\u0947\u0935\u0902 \u090b\u0924\u094d\u0935\u093f\u091c\u092e\u094d | "
            "\u0939\u094b\u0924\u093e\u0930\u0902 \u0930\u0924\u094d\u0928\u0927\u093e\u0924\u092e\u092e\u094d ||"
        )
        self.assertEqual(len(payload["padas"]), 3)
        self.assertEqual([pada["syllable_count"] for pada in payload["padas"]], [8, 8, 8])
        self.assertEqual(payload["overall_stanza_meter"], "G\u0101yatr\u012b \u2014 24-syllable Vedic matrix")

    def test_short_eight_syllable_fragment_is_not_full_meter(self):
        payload = analyze_sanskrit("\u0939\u094b\u0924\u093e\u0930\u0902 \u0930\u0924\u094d\u0928\u0927\u093e\u0924\u092e\u092e\u094d")
        self.assertEqual(len(payload["padas"]), 1)
        self.assertEqual(payload["padas"][0]["syllable_count"], 8)
        self.assertNotIn("Anu\u1e63\u1e6dubh", payload["overall_stanza_meter"])
        self.assertNotIn("G\u0101yatr\u012b", payload["overall_stanza_meter"])

    def test_newline_segmentation_creates_primary_segments(self):
        payload = analyze_sanskrit("rama rama rama rama\nrama rama rama rama")
        self.assertEqual(len(payload["pada_segments"]), 2)

    def test_avagraha_is_null_marker_for_syllable_scan(self):
        payload = analyze_sanskrit("\u0935\u0930\u0941\u0923\u094b\u093d\u0917\u094d\u0928\u093f\u0903")
        diagnostics = " ".join(item["message"] for item in payload["parser_diagnostics"])
        self.assertNotIn("U+093D", diagnostics)
        self.assertGreater(payload["total_matra_count"], 0)

    def test_empty_and_malformed_unicode_inputs_do_not_crash(self):
        empty = analyze_sanskrit("")
        malformed = analyze_sanskrit("\ud800")
        self.assertEqual(empty["total_matra_count"], 0)
        self.assertEqual(empty["padas"], [])
        self.assertTrue(empty["parser_diagnostics"])
        self.assertTrue(malformed["parser_diagnostics"])

    def test_api_errors_map_to_sanskrit_tab_exception_contract(self):
        client = TestClient(app)
        response = client.post("/api/v3/analyze", json={"input_text": "a" * 2001})
        self.assertEqual(response.status_code, 400)
        detail = response.json()["detail"]
        self.assertEqual(detail["code"], "invalid_sanskrit_input")
        self.assertIn("parser_diagnostics", detail)

    def test_experimental_payload_is_isolated_from_classical_payload(self):
        payload = analyze_sanskrit("agnim ile")
        classical_keys = {
            "unicode_clusters",
            "transliteration",
            "sandhi",
            "overall_stanza_meter",
            "total_matra_count",
            "padas",
            "phonological_syllables",
            "derivation_history",
            "prakriya_graph",
            "lexical_lookup",
            "parser_diagnostics",
        }
        for key in classical_keys:
            self.assertNotIn("field_map", payload[key] if isinstance(payload[key], dict) else {})
        self.assertIn("field_map", payload["experimental_payload"])

    def test_unknown_linguistic_metadata_is_not_guessed(self):
        payload = analyze_sanskrit("unknownword")
        self.assertIsNone(payload["lexical_lookup"][0]["gender"])
        self.assertIsNone(payload["lexical_lookup"][0]["source"])
        self.assertEqual(payload["lexical_source_governance"], LEXICAL_SOURCE_GOVERNANCE)

    def test_candidate_ceiling_limits_ambiguity_growth(self):
        payload = analyze_sanskrit(" ".join(["rama"] * 400))
        self.assertLessEqual(len(payload["padas"]), 96)
        self.assertLessEqual(len(payload["phonological_syllables"]), 256)

    def test_vyakarana_final_form_cleanup_uses_current_state(self):
        self.assertEqual(final_form_cleanup("agnim   ile, "), "agnim ile")
        payload = analyze_sanskrit("agnim ile")
        self.assertEqual(payload["derivation_history"][-1]["stage"], "final-form cleanup")

    def test_sanskrit_tab_has_required_render_targets(self):
        view = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        for target in [
            "overall-stanza-meter",
            "total-matra-count",
            "padas-output",
            "phonological-syllables-output",
            "derivation-history-output",
            "experimental-payload-output",
        ]:
            self.assertIn(target, view)
        self.assertIn("Experimental Symbolic Structural Projection Field Map", view)

    def test_no_invalid_tailwind_or_ingress_fragments_exist(self):
        searchable = [
            ROOT / "index.html",
            ROOT / "shared" / "master.css",
            ROOT / "ui" / "tabs" / "sanskrit" / "style.css",
            ROOT / "vercel.json",
        ]
        for path in searchable:
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("jsdelivr.net", source)
            self.assertNotIn("@theme", source)
            self.assertNotIn("host: ://enterprise.com", source)


if __name__ == "__main__":
    unittest.main()
