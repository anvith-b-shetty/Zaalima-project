
import pytest

from scientific_discovery.agents.experiment_designer.code_generator import (
    validate_experiment_code
)


def test_valid_python_code_is_accepted():
    code = """
values = [10, 20, 30]
print(sum(values) / len(values))
"""

    validate_experiment_code(code)


def test_import_statement_is_rejected():
    with pytest.raises(ValueError, match="Imports are not allowed"):
        validate_experiment_code("import os")


def test_empty_code_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        validate_experiment_code("")


def test_file_access_is_rejected():
    code = "open('test.txt')"

    with pytest.raises(ValueError, match="not approved"):
        validate_experiment_code(code)


def test_attribute_access_is_rejected():
    code = "values.append(10)"

    with pytest.raises(
        ValueError,
        match="Only direct function calls are allowed"
    ):
        validate_experiment_code(code)


def test_invalid_python_syntax_is_rejected():
    code = "if True print('Hello')"

    with pytest.raises(ValueError, match="Invalid Python syntax"):
        validate_experiment_code(code)
