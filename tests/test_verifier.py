"""Parser, verificador y reward: equivalencias aceptadas y ataques rechazados."""

import json
import unittest

from challenge.generator import generate
from challenge.parser import extract_answer, number, words_to_number
from challenge.units import canonical_unit
from challenge.verifier import MAX_CHARS, reward, verify

# v = 110 m / 5 s = 22 m/s
SPEED = {
    "family": "speed",
    "given": {"d": [110.0, "m"], "t": [5.0, "s"]},
    "requested_unit": "m/s",
}
SPEED_KMH = {**SPEED, "requested_unit": "km/h"}  # 79.2 km/h


class Units(unittest.TestCase):
    def test_aliases_map_to_same_unit_only(self):
        for text, unit in (
            ("km/h", "km/h"), ("Km/h", "km/h"), ("kph", "km/h"), ("km h⁻¹", "km/h"),
            ("kilómetros por hora", "km/h"), ("kilometros por hora", "km/h"),
            ("m·s^-1", "m/s"), ("metros por segundo", "m/s"), ("joule", "J"),
            ("Julios", "J"), ("KJ", "kJ"), ("vatios", "W"), ("erg s^{-1}", "erg/s"),
        ):  # fmt: skip
            with self.subTest(text=text):
                self.assertEqual(canonical_unit(text), unit)
        for text in ("kWh", "mJ", "MJ", "kg/s", "J/s", ""):
            self.assertIsNone(canonical_unit(text))


class Numbers(unittest.TestCase):
    def test_thousands_separator_is_ambiguous(self):
        for text in ("3,380", "1,000", "41,879", "-2,500"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                number(text)
        self.assertEqual(number("0.125"), 0.125)
        self.assertEqual(number("22,0"), 22.0)
        self.assertEqual(number("3380"), 3380)
        self.assertEqual(number("3.38"), 3.38)
        self.assertEqual(number("3.380"), 3.38)  # punto siempre decimal
        self.assertEqual(number("985.203"), 985.203)
        self.assertEqual(number("22,5"), 22.5)
        self.assertEqual(number("2,2 × 10^1"), 22.0)

    def test_number_words(self):
        for words, value in (
            ("cuarenta", 40), ("veintidós", 22), ("cuarenta y dos", 42),
            ("ciento veinte", 120), ("dos mil quinientos", 2500),
            ("forty-two", 42), ("one hundred twenty", 120), ("cero", 0),
        ):  # fmt: skip
            with self.subTest(words=words):
                self.assertEqual(words_to_number(words.split()), value)
        for words in ("y", "cuarenta y", "metros", "dos tres x"):
            self.assertIsNone(words_to_number(words.split()))


class Verify(unittest.TestCase):
    def test_equivalent_surface_forms_are_correct(self):
        for completion in (
            "FINAL: 22 m/s",
            '**FINAL:** {"value": 22, "unit": "m/s"}',
            'La respuesta final es: {"value": 22, "unit": "m/s"}',
            '```json\n{"value": 22, "unit": "m/s"}\n```',
            "v = 110 / 5 = 22 m/s",
            "La respuesta final es 22,0 m/s.",
            "FINAL: 2,2 × 10^1 m/s",
            "FINAL: 2.2 \\cdot 10^{1} m/s",
            "FINAL: 2.2×10¹ m/s",
            '{"value": "2,2*10^1", "unit": "m/s"}',
            'Velocidad = 22 m/s. {"value": 22, "unit": "m/s"}',
            "$ \\boxed{22} \\text{ m/s} $",
            'Calculamos velocidad final:\nFINAL: {"value": 22, "unit": "m/s"}',
            'Respuesta: {"v": 22, "unidad": "m/s"}',
            "Respuesta numérica: **22**; unidad: **m/s**.",
            "Respuesta numérica: 22\nUnidad: m/s",
            "Respuesta numérica: $ 22 \\, \\text{m/s} $\n\nUnidad: $ \\text{m/s} $",
            "La velocidad del móvil es de aproximadamente 22 m/s.",
            "Por lo tanto, la velocidad es de 22 metros por segundo.",
            "22m/s",
            "FINAL: 22 m·s⁻¹",
            "Respuesta final:\n$$\n\\boxed{22} \\, \\text{m/s}\n$$",
            'Respuesta: {"v": "22 m/s"}',
            "Respuesta: 22 m/s, unidad: m/s.",
            'FINAL: {"value": 22, "unit": "m/s"}\nRespuesta numérica y unidad:\n22 m/s',
            "FINAL: veintidós metros por segundo",
            "La rapidez es de twenty-two m/s",
            "<think>d/t = 110/5</think>\nFINAL: 22 m/s",
            "FINAL: 22.2 m/s",  # dentro del 1%
        ):
            with self.subTest(completion=completion):
                self.assertEqual(verify(SPEED, completion), "correct")
        for completion in ("FINAL: 79.2 km/h", "FINAL: 79.2 kph", "79.2 kms/h"):
            self.assertEqual(verify(SPEED_KMH, completion), "correct")

    def test_requested_unit_is_required(self):
        # Cantidad físicamente equivalente en otra unidad: no basta.
        self.assertEqual(verify(SPEED_KMH, "FINAL: 22 m/s"), "unit")
        self.assertEqual(verify(SPEED, "FINAL: 79.2 km/h"), "unit")
        self.assertEqual(verify(SPEED, "FINAL: 22 kg"), "unit")

    def test_wrong_value_is_numeric(self):
        self.assertEqual(verify(SPEED, "FINAL: 0 m/s"), "numeric")
        self.assertEqual(verify(SPEED, "FINAL: 22.3 m/s"), "numeric")
        self.assertEqual(verify(SPEED, "Desarrollo: 22 m/s\nFINAL: 0 m/s"), "numeric")

    def test_hacks_and_ambiguity_get_no_reward(self):
        for completion in (
            # varias respuestas / alternativas
            '{"value": 0, "unit": "m/s"}\n{"value": 22, "unit": "m/s"}',
            'FINAL: {"value": 22, "unit": "m/s"}\nFINAL: {}',
            "22 m/s o 0 m/s",
            "22 m/s\n0 m/s",
            "FINAL: 22 m/s\n0 m/s",
            "FINAL: 22 m/s\nFINAL: 0 m/s",
            'FINAL: {"value": 22, "unit": "m/s"} o 0 m/s',
            '22 m/s o {"value": 0, "unit": "m/s"}',
            "FINAL: 0 m/s\n" + '{"value": 22, "unit": "m/s"}',
            "Respuesta: 0 m/s. " + '{"value": 22, "unit": "m/s"}',
            "0 m/s\n" + '{"value": 22, "unit": "m/s"}',
            'FINAL: {"value": 22, "unit": "m/s"}\nRespuesta numérica y unidad:\n0 m/s',
            "Respuesta: 22 m/s, unidad: km/h.",
            "FINAL: entre 21 y 23 m/s",
            "FINAL: 22 m/s y 0 m/s",
            "FINAL: 0 m/s\nRevisando, v = 22 m/s",
            "Respuesta: 0 m/s\nAunque en realidad son 22 m/s",
            # formato JSON explotable
            'FINAL: {"value": 0, "value": 22, "unit": "m/s"}',
            'FINAL: [{"value": 22, "unit": "m/s"}]',
            'FINAL: {"value": true, "unit": "m/s"}',
            'FINAL: {"value": NaN, "unit": "m/s"}',
            'FINAL: {"value": [22], "unit": "m/s"}',
            'FINAL: {"value": 22, "unit": "m/s", "other": 0}',
            'FINAL: {"value": 22, "unit": "m/s"} extra',
            'FINAL: {"value": "__import__(\'os\')", "unit": "m/s"}',
            # sin unidad, sin cierre, expresiones sin evaluar
            "FINAL: 22",
            "FINAL: 1e3",
            "FINAL: 110/5 m/s",
            "<think>FINAL: 22 m/s",
            "",
        ):
            with self.subTest(completion=completion):
                self.assertNotEqual(verify(SPEED, completion), "correct")
                self.assertIn(verify(SPEED, completion), ("unparsed", "unit"))

    def test_thousands_separator_regression(self):
        energy = {
            "family": "energy",
            "given": {"m": [2.0, "kg"], "v": [58.137767414994535, "m/s"]},
            "requested_unit": "J",
        }  # 3380 J
        # Llama escribió "3.380 J" queriendo decir 3380: viola el formato pedido.
        self.assertEqual(verify(energy, "FINAL: 3.380 J"), "numeric")
        self.assertEqual(verify(energy, "FINAL: 3,380 J"), "unparsed")
        self.assertEqual(verify(energy, "FINAL: 3380 J"), "correct")
        self.assertEqual(verify(energy, "FINAL: 3.38e3 J"), "correct")

    def test_length_cap(self):
        padding = "a" * MAX_CHARS
        self.assertEqual(verify(SPEED, padding + "\nFINAL: 22 m/s"), "too_long")

    def test_extract_returns_canonical_unit(self):
        self.assertEqual(extract_answer("FINAL: 4.07e-6 W"), (4.07e-6, "W"))
        self.assertEqual(extract_answer("FINAL: 3 kph"), (3.0, "km/h"))


class Reward(unittest.TestCase):
    def test_reward_interface_on_generated_tasks(self):
        for task in generate("eval", 3):
            answer, unit = task["answer"], task["requested_unit"]
            self.assertEqual(reward(task["prompt"], f"FINAL: {answer:.6g} {unit}"), 1.0)
            self.assertEqual(reward(task["prompt"], f"FINAL: {answer * 2:.6g} {unit}"), 0.0)
            self.assertEqual(
                reward(task["prompt"], json.dumps({"value": answer, "unit": unit})), 1.0
            )

    def test_reward_never_raises(self):
        for prompt in ("", "sin datos", "x\nDATOS: {", 'x\nDATOS: {"family": "nope"}'):
            self.assertEqual(reward(prompt, "FINAL: 22 m/s"), 0.0)
        task = generate("eval", 1)[0]
        for completion in ("", "{" * 10_000, "[" * 3000, "9" * 3000 + " m/s"):
            self.assertEqual(reward(task["prompt"], completion), 0.0)

    def test_prompt_data_block_has_no_answer(self):
        for task in generate("eval", 5):
            data = task["prompt"].rsplit("\nDATOS: ", 1)[1]
            self.assertEqual(set(json.loads(data)), {"family", "given", "requested_unit"})


if __name__ == "__main__":
    unittest.main()
