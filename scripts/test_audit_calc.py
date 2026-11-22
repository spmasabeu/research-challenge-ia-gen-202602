import unittest

import audit_calc


def flags(text):
    return [row[0] for row in audit_calc.check_equalities(text)]


class AuditCalcTests(unittest.TestCase):
    def test_rounding_is_ok_and_wrong_digits_are_flagged(self):
        self.assertEqual(flags("10/3 = 3.33"), ["OK"])
        self.assertEqual(flags("10/3 = 3.31"), ["ERROR"])
        self.assertEqual(flags("16.6/0.92 = 18.1"), ["DESVIO"])

    def test_exact_truncation_is_distinguished_from_wrong_last_digit(self):
        self.assertEqual(flags("5618/164 = 34.25"), ["TRUNC"])
        self.assertEqual(flags("4454/92 = 48.5"), ["DESVIO"])

    def test_unit_conversions_are_checked(self):
        self.assertEqual(flags("Convertimos 2 km = 200 m."), ["ERROR"])
        self.assertEqual(flags("6.702 kN = 6702 N"), ["OK"])

    def test_multistep_conversion_compares_start_and_end_quantities(self):
        rows = audit_calc.check_equalities("v = 53.28 km/h = 53.28 / 3.6 ≈ 14.7944 m/s")
        self.assertIn("conversión km/h→m/s", [row[1] for row in rows])
        self.assertTrue(all(row[0] == "DESVIO" for row in rows))

    def test_subscripts_exponents_and_bullets_are_not_numbers(self):
        self.assertEqual(flags("m1 = 3060 g = 3.06 kg, m2 = 2040 g = 2.04 kg"), ["OK", "OK"])
        self.assertEqual(flags("E = v^2 / 2 = 5"), [])
        self.assertEqual(flags("- $ 6082.135 \\times 0.49 \\approx 2982.256 $"), ["DESVIO"])

    def test_latex_fractions_are_evaluated(self):
        text = "$ E = \\frac{25.1 \\cdot 1303.61}{2} = \\frac{32705.1}{2} = 16352.55 $ J"
        self.assertEqual(flags(text), ["DESVIO", "OK"])

    def test_expected_value_sums_paired_magnitudes_and_converts_target(self):
        row = {
            "family": "pressure",
            "prompt": "Datos: F1=0.45 kN; F2=1.05 kN; A=0.25 m^2\n"
            "Expresa el resultado en kPa. Explica",
        }
        data, si, target = audit_calc.expected_from_prompt(row)
        self.assertEqual(target, "kPa")
        self.assertAlmostEqual(si, 6000.0)
        self.assertEqual(set(data), {"F1", "F2", "A"})

    def test_final_answer_reads_last_json(self):
        text = 'x {"value": 1, "unit": "J"} y {"value": 0.0874, "unit": "kJ"}'
        self.assertEqual(audit_calc.final_answer(text), (0.0874, "kJ"))


if __name__ == "__main__":
    unittest.main()
