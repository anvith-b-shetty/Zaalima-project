REQUIRED_FIELDS = [
    "sample_id",
    "temperature_c",
    "pH",
    "enzyme_activity_u_ml",
]


def validate_experiment_results(result):
    """Validate parsed experiment records and return issues found."""

    issues = []
    records = result.get("records")

    if not isinstance(records, list):
        return {
            "valid": False,
            "record_count": 0,
            "issues": ["'records' must be a list."],
        }

    if not records:
        issues.append("No experiment records were provided.")

    seen_sample_ids = set()

    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            issues.append(f"Record {index} must be an object.")
            continue

        missing_fields = [
            field for field in REQUIRED_FIELDS
            if field not in record
        ]

        if missing_fields:
            issues.append(
                f"Record {index} is missing: {', '.join(missing_fields)}."
            )
            continue

        sample_id = record["sample_id"]

        if not isinstance(sample_id, str) or not sample_id.strip():
            issues.append(f"Record {index} has an empty or invalid sample_id.")
        elif sample_id in seen_sample_ids:
            issues.append(f"Duplicate sample_id: {sample_id}.")
        else:
            seen_sample_ids.add(sample_id)

        numeric_fields = [
            "temperature_c",
            "pH",
            "enzyme_activity_u_ml",
        ]

        numeric_values_valid = True

        for field in numeric_fields:
            value = record[field]

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                issues.append(
                    f"Record {index}: '{field}' must be numeric."
                )
                numeric_values_valid = False

        if not numeric_values_valid:
            continue

        if record["temperature_c"] < -273.15:
            issues.append(
                f"Record {index}: temperature is below absolute zero."
            )

        if not 0 <= record["pH"] <= 14:
            issues.append(
                f"Record {index}: pH must be between 0 and 14."
            )

        if record["enzyme_activity_u_ml"] < 0:
            issues.append(
                f"Record {index}: enzyme activity cannot be negative."
            )

    return {
        "valid": len(issues) == 0,
        "record_count": len(records),
        "issues": issues,
    }