"""D6 regression checks using recorded evidence only."""
import copy
from decimal import Decimal as D
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import cost_to_serve as c


class Costs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = c.build()
        cls.raw = json.loads((c.ROOT/c.INPUTS[1]).read_text())

    def test_five_families(self):
        self.assertEqual([r["model"] for r in self.data["models"]], list(c.MODELS))
        self.assertNotIn("openai/gpt-4.1-mini", c.MODELS)

    def test_all_complete(self):
        for model, path in zip(c.MODELS,c.INPUTS):
            self.assertEqual(len(c.validate(json.loads((c.ROOT/path).read_text()),model)),60)

    def test_verdicts(self):
        self.assertEqual([r["code_check_passed"] for r in self.data["models"]],[48,51,49,45,22])

    def test_provider_bills(self):
        self.assertEqual([r["provider_comparison"]["recorded_battery_usd"] for r in self.data["models"]],
                         [.736601,.097416,.189767,.064365,.015020])

    def test_independent_raw_decimal_all_models(self):
        for e in self.data["models"]:
            rows=json.loads((c.ROOT/e["source"]).read_text())["results"]
            price=self.data["prices"]["models"][e["model"]]
            total=sum((D(str(r["record"]["tokens_in"]))*D(price["prompt"])+
                       D(str(r["record"]["tokens_out"]))*D(price["completion"]) for r in rows),D(0))
            self.assertAlmostEqual(float(total),e["layer_1"]["list_token_total_usd"],places=10)
            expected=(total/60+D(sum(not r["passed"] for r in rows))/60*D(55)/6)*4000
            self.assertAlmostEqual(float(expected),e["monthly"]["total_usd"],places=8)

    def test_deepseek_baseline(self):
        b=self.data["models"][1]
        self.assertEqual(b["layer_1"]["variable_per_referral_usd"],.00209375)
        self.assertEqual(b["monthly"]["total_usd"],5508.375)

    def test_upstream_reconciliation(self):
        expected=[7385.11,5508.49,6737.32,9174.29,23231.67]
        for row,want in zip(self.data["models"],expected):
            self.assertAlmostEqual(round(row["provider_comparison"]["old_provider_and_rounded_fallback_monthly_usd"],2),want)

    def test_fixed_fee_once(self):
        a=c.course.monthly(.01,.9,float(c.F),4000,0)
        b=c.course.monthly(.01,.9,float(c.F),4000,100)
        self.assertAlmostEqual(b-a,100)

    def test_partial_rejected(self):
        d=copy.deepcopy(self.raw);d["results"]=d["results"][:9];d["complete"]=False
        with self.assertRaises(ValueError):c.validate(d,c.MODELS[1])

    def test_duplicate_rejected(self):
        d=copy.deepcopy(self.raw);d["results"][-1]=copy.deepcopy(d["results"][0])
        with self.assertRaises(ValueError):c.validate(d,c.MODELS[1])

    def test_model_mismatch(self):
        with self.assertRaises(ValueError):c.validate(self.raw,c.MODELS[0])

    def test_usage_missing(self):
        d=copy.deepcopy(self.raw);d["results"][0]["record"]["cost_usd"]=None
        with self.assertRaises(ValueError):c.validate(d,c.MODELS[1])

    def test_missing_verdict(self):
        d=copy.deepcopy(self.raw);d["results"][0]["passed"]=None
        with self.assertRaises(ValueError):c.validate(d,c.MODELS[1])

    def test_fractional_tokens(self):
        d=copy.deepcopy(self.raw);d["results"][0]["record"]["tokens_in"]=1.2
        with self.assertRaises(ValueError):c.validate(d,c.MODELS[1])

    def test_invalid_numbers(self):
        for x in [None,True,-1,"NaN","Infinity"]:
            with self.subTest(x=x),self.assertRaises(ValueError):c.dec(x)

    def test_gpt_separate_and_clipped(self):
        s=self.data["recommended_model_separate"]["sensitivity"]
        self.assertEqual([r["assumed_success_rate"] for r in s],[.85,.95,1.0])
        self.assertTrue(s[-1]["clipped"])

    def test_deepseek_sensitivity(self):
        s=self.data["models"][1]["sensitivity"]
        self.assertEqual([r["assumed_success_rate"] for r in s],[.75,.85,.95])
        self.assertAlmostEqual(s[0]["monthly_total_usd"]-s[1]["monthly_total_usd"],3666.666666667,places=7)

    def test_break_even(self):
        b=self.data["break_even"]
        cheap=self.data["models"][4]["layer_1"]["variable_per_referral_usd"]
        e=self.data["models"][1]["expected_total_per_referral_usd"]
        self.assertAlmostEqual(cheap+(1-b["required_cheap_success_rate"])*float(c.F),e,places=9)

    def test_serialized_output(self):
        self.assertEqual(json.loads((c.ROOT/"evidence/d6_cost_to_serve.json").read_text()),self.data)

    def test_reconciliation_decomposition(self):
        for m in self.data["models"]:
            x=m["provider_comparison"]
            self.assertAlmostEqual(x["new_baseline_minus_old_monthly_usd"],
                                   x["list_repricing_monthly_effect_usd"]+x["exact_labour_monthly_effect_usd"],places=8)

    def test_raw_sources_unchanged(self):
        import hashlib
        for path, sha in self.data["source_sha256"].items():
            self.assertEqual(hashlib.sha256((c.ROOT/path).read_bytes()).hexdigest(),sha)

    def test_report_under_budget(self):
        body=(c.ROOT/"docs/D6_SECTION4_REPORT.md").read_text().split("\n\n",1)[1]
        self.assertLessEqual(len(body.split()),400)
        self.assertIn("US$5,508.38",body)

    def test_foreign_cwd(self):
        with tempfile.TemporaryDirectory() as p:
            r=subprocess.run([sys.executable,str(c.ROOT/"cost_to_serve.py"),"--check"],cwd=p,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)


if __name__=="__main__":
    unittest.main()
