import csv
import json
from pathlib import Path


REQUIRED_COLUMNS = [
    "sample_id",
    "temperature_c",
    "pH",
    "enzyme_activity_u_ml",
]


def parse_experiment_results(csv_path, output_path=None):
    """Parse enzyme experiment results from a CSV file."""

    csv_path = Path(csv_path)

    if not csv_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    if csv_path.suffix.lower() != ".csv":
        raise ValueError("Input file must be a CSV.")

    records = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV is empty or has no header row.")

        missing_columns = [
            column for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                sample_id = row["sample_id"].strip()

                if not sample_id:
                    raise ValueError("sample_id is empty")

                record = {
                    "sample_id": sample_id,
                    "temperature_c": float(row["temperature_c"]),
                    "pH": float(row["pH"]),
                    "enzyme_activity_u_ml": float(
                        row["enzyme_activity_u_ml"]
                    ),
                }

                records.append(record)

            except (AttributeError, TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid data on CSV row {row_number}: {error}"
                ) from error

    result = {
        "source_file": csv_path.name,
        "record_count": len(records),
        "units": {
            "temperature_c": "°C",
            "pH": "unitless",
            "enzyme_activity_u_ml": "U/mL",
        },
        "records": records,
    }

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

        print(f"Parsed results saved to: {output_path}")

    return result