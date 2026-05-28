import json
import subprocess
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_node_json(source):
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", source],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    return json.loads(completed.stdout)


class TinantaGeneratorEngineTests(unittest.TestCase):
    def generate_forms(self, dhatu):
        source = textwrap.dedent(
            f"""
            import {{ generateTinanta }} from './ui/tabs/sanskrit/tinanta/tinanta-generator-engine.js';
            const purushas = ['prathama', 'madhyama', 'uttama'];
            const vacanas = ['eka', 'dvi', 'bahu'];
            const forms = {{}};
            for (const purusha of purushas) {{
              for (const vacana of vacanas) {{
                const output = generateTinanta({{
                  dhatu: '{dhatu}',
                  lakara: 'laṭ',
                  pada: 'parasmaipada',
                  purusha,
                  vacana,
                }});
                forms[`${{purusha}}.${{vacana}}`] = output.generatedForm;
              }}
            }}
            console.log(JSON.stringify(forms));
            """
        )
        return run_node_json(source)

    def test_bhu_lat_parasmaipada_all_forms(self):
        result = self.generate_forms("bhū")
        self.assertEqual(
            result,
            {
                "prathama.eka": "bhavati",
                "prathama.dvi": "bhavataḥ",
                "prathama.bahu": "bhavanti",
                "madhyama.eka": "bhavasi",
                "madhyama.dvi": "bhavathaḥ",
                "madhyama.bahu": "bhavatha",
                "uttama.eka": "bhavāmi",
                "uttama.dvi": "bhavāvaḥ",
                "uttama.bahu": "bhavāmaḥ",
            },
        )

    def test_gam_lat_parasmaipada_all_forms(self):
        result = self.generate_forms("gam")
        self.assertEqual(
            result,
            {
                "prathama.eka": "gacchati",
                "prathama.dvi": "gacchataḥ",
                "prathama.bahu": "gacchanti",
                "madhyama.eka": "gacchasi",
                "madhyama.dvi": "gacchathaḥ",
                "madhyama.bahu": "gacchatha",
                "uttama.eka": "gacchāmi",
                "uttama.dvi": "gacchāvaḥ",
                "uttama.bahu": "gacchāmaḥ",
            },
        )

    def test_ni_lat_parasmaipada_all_forms(self):
        result = self.generate_forms("nī")
        self.assertEqual(
            result,
            {
                "prathama.eka": "nayati",
                "prathama.dvi": "nayataḥ",
                "prathama.bahu": "nayanti",
                "madhyama.eka": "nayasi",
                "madhyama.dvi": "nayathaḥ",
                "madhyama.bahu": "nayatha",
                "uttama.eka": "nayāmi",
                "uttama.dvi": "nayāvaḥ",
                "uttama.bahu": "nayāmaḥ",
            },
        )

    def test_reverse_lookup(self):
        source = textwrap.dedent(
            """
            import { reverseTinanta } from './ui/tabs/sanskrit/tinanta/tinanta-generator-engine.js';
            const forms = {
              bhavati: reverseTinanta('bhavati').reconstructed,
              gacchati: reverseTinanta('gacchati').reconstructed,
              nayati: reverseTinanta('nayati').reconstructed,
            };
            console.log(JSON.stringify(forms));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["bhavati"], {"dhatu": "bhū", "lakara": "laṭ", "pada": "parasmaipada", "purusha": "prathama", "vacana": "eka"})
        self.assertEqual(result["gacchati"], {"dhatu": "gam", "lakara": "laṭ", "pada": "parasmaipada", "purusha": "prathama", "vacana": "eka"})
        self.assertEqual(result["nayati"], {"dhatu": "nī", "lakara": "laṭ", "pada": "parasmaipada", "purusha": "prathama", "vacana": "eka"})

    def test_paradigm_generation(self):
        source = textwrap.dedent(
            """
            import { generateTinantaParadigm } from './ui/tabs/sanskrit/tinanta/tinanta-generator-engine.js';
            const counts = {
              bhu: generateTinantaParadigm({ dhatu: 'bhū', lakara: 'laṭ', pada: 'parasmaipada' }).forms.length,
              gam: generateTinantaParadigm({ dhatu: 'gam', lakara: 'laṭ', pada: 'parasmaipada' }).forms.length,
              ni: generateTinantaParadigm({ dhatu: 'nī', lakara: 'laṭ', pada: 'parasmaipada' }).forms.length,
            };
            console.log(JSON.stringify(counts));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, {"bhu": 9, "gam": 9, "ni": 9})

    def test_runtime_isolation_no_input_mutation(self):
        source = textwrap.dedent(
            """
            import { generateTinanta } from './ui/tabs/sanskrit/tinanta/tinanta-generator-engine.js';
            const input = {
              dhatu: 'bhū',
              lakara: 'laṭ',
              pada: 'parasmaipada',
              purusha: 'prathama',
              vacana: 'eka',
              metadata: { source: 'test' },
            };
            const before = JSON.stringify(input);
            const output = generateTinanta(input);
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, form: output.generatedForm }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertEqual(result["form"], "bhavati")

    def test_stability(self):
        source = textwrap.dedent(
            """
            import { generateTinanta } from './ui/tabs/sanskrit/tinanta/tinanta-generator-engine.js';
            const input = { dhatu: 'gam', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'uttama', vacana: 'bahu' };
            const first = generateTinanta(input);
            const second = generateTinanta(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_unsupported_safety(self):
        source = textwrap.dedent(
            """
            import { generateTinanta } from './ui/tabs/sanskrit/tinanta/tinanta-generator-engine.js';
            const cases = [
              generateTinanta({ dhatu: 'bhū', lakara: 'liṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' }),
              generateTinanta({ dhatu: 'bhū', lakara: 'laṭ', pada: 'atmanepada', purusha: 'prathama', vacana: 'eka' }),
              generateTinanta({ dhatu: 'pac', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' }),
              generateTinanta({ dhatu: 'bhū', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'unknown', vacana: 'eka' }),
              generateTinanta({ dhatu: 'bhū', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'unknown' }),
            ];
            console.log(JSON.stringify(cases.map((item) => item.diagnostics.supported)));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, [False, False, False, False, False])

    def test_partial_input_safety(self):
        source = textwrap.dedent(
            """
            import { generateTinanta } from './ui/tabs/sanskrit/tinanta/tinanta-generator-engine.js';
            const outputs = [
              generateTinanta(),
              generateTinanta(null),
              generateTinanta({}),
              generateTinanta({ dhatu: null, lakara: null, pada: null, purusha: null, vacana: null }),
              generateTinanta({ dhatu: '', lakara: '', pada: '', purusha: '', vacana: '' }),
            ];
            console.log(JSON.stringify(outputs.map((item) => item.status)));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, ["ready", "ready", "ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()
