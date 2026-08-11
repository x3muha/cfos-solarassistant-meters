import json
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[1]
MQTT_DIR = ROOT / "meters" / "mqtt"


class MeterProfileTest(TestCase):
    def test_all_meter_files_are_valid_json(self):
        for path in sorted((ROOT / "meters").glob("**/*.json")):
            with self.subTest(path=path.relative_to(ROOT)):
                with path.open(encoding="utf-8") as handle:
                    self.assertIsInstance(json.load(handle), dict)

    def test_mqtt_profiles_contain_topics_but_no_credentials(self):
        paths = sorted(MQTT_DIR.glob("*.json"))
        self.assertEqual(len(paths), 4)

        for path in paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                profile = json.loads(text)
                self.assertEqual(profile["rtype"], 2)
                self.assertNotIn("://", text)
                self.assertNotIn("password", text.lower())
                self.assertNotIn("username", text.lower())

                fields = [
                    value
                    for value in profile.values()
                    if isinstance(value, dict) and "address" in value
                ]
                self.assertGreater(len(fields), 0)
                for field in fields:
                    self.assertTrue(field["address"].startswith("solar_assistant/"))
                    self.assertTrue(field["address"].endswith("/state"))

    def test_mqtt_profiles_do_not_claim_missing_energy_totals(self):
        for path in sorted(MQTT_DIR.glob("*.json")):
            with self.subTest(path=path.name):
                profile = json.loads(path.read_text(encoding="utf-8"))
                self.assertNotIn("import_wh", profile)
                self.assertNotIn("export_wh", profile)


if __name__ == "__main__":
    main()
