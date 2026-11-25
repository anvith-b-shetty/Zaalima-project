import tempfile
import unittest
from pathlib import Path

from src.scientific_discovery.multimodal.experiment_result_parser import (
    parse_experiment_results,
)
from src.scientific_discovery.multimodal.experiment_result_validator import (
    validate_experiment_results,
)


class ExperimentResultTests(unittest.TestCase):
    def test_parse_valid_csv(self):
        csv_text = (
            "sample_id,temperature_c,pH,enzyme_activity_u_ml\n"
            "S-001,20,6.5,12.4\n"
            "S-002,25,6.5,18.7\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "results.csv"
            csv_path.write_text(csv_text, encoding="utf-8")

            result = parse_experiment_results(str(csv_path))

        self.assertEqual(result["record_count"], 2)
        self.assertEqual(len(result["records"]), 2)

    def test_validator_rejects_invalid_values(self):
        result = {
            "records": [
                {
                    "sample_id": "S-001",
                    "temperature_c": 20,
                    "pH": 15,
                    "enzyme_activity_u_ml": -1,
                }
            ]
        }

        validation = validate_experiment_results(result)

        self.assertFalse(validation["valid"])
        self.assertTrue(validation["issues"])


if __name__ == "__main__":
    unittest.main()
