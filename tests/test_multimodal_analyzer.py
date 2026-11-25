import json
import tempfile
import unittest
from pathlib import Path

from src.scientific_discovery.multimodal.multimodal_analyzer import (
    analyze_multimodal_data,
)


class MultimodalAnalyzerTests(unittest.TestCase):
    def test_combines_figures_and_tables_by_page(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            figure_path = temp / "figures.json"
            table_path = temp / "tables.json"
            output_path = temp / "combined.json"

            figure_data = {
                "filename": "paper.pdf",
                "total_pages": 2,
                "total_images": 1,
                "pages": [
                    {
                        "page_number": 1,
                        "image_count": 1,
                        "images": [{"image_id": "fig-1"}],
                    },
                    {
                        "page_number": 2,
                        "image_count": 0,
                        "images": [],
                    },
                ],
            }

            table_data = {
                "filename": "paper.pdf",
                "total_pages": 2,
                "total_tables": 1,
                "pages": [
                    {
                        "page_number": 1,
                        "table_count": 0,
                        "tables": [],
                    },
                    {
                        "page_number": 2,
                        "table_count": 1,
                        "tables": [{"table_id": "table-1"}],
                    },
                ],
            }

            figure_path.write_text(
                json.dumps(figure_data), encoding="utf-8"
            )
            table_path.write_text(
                json.dumps(table_data), encoding="utf-8"
            )

            result = analyze_multimodal_data(
                figure_path, table_path, output_path
            )

            self.assertEqual(result["total_pages"], 2)
            self.assertEqual(result["pages"][0]["image_count"], 1)
            self.assertEqual(result["pages"][1]["table_count"], 1)
            self.assertTrue(output_path.is_file())

    def test_rejects_different_pdf_filenames(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            figure_path = temp / "figures.json"
            table_path = temp / "tables.json"

            figure_data = {
                "filename": "paper_a.pdf",
                "total_pages": 1,
                "total_images": 0,
                "pages": [],
            }
            table_data = {
                "filename": "paper_b.pdf",
                "total_pages": 1,
                "total_tables": 0,
                "pages": [],
            }

            figure_path.write_text(
                json.dumps(figure_data), encoding="utf-8"
            )
            table_path.write_text(
                json.dumps(table_data), encoding="utf-8"
            )

            with self.assertRaises(ValueError):
                analyze_multimodal_data(figure_path, table_path)


if __name__ == "__main__":
    unittest.main()
