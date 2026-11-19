
import pymupdf
import json
from pathlib import Path


def extract_cell_text(page, cell):
    """
    Extract text from a table cell using its coordinates.
    """

    if cell is None:
        return ""

    rect = pymupdf.Rect(cell)

    words = page.get_text(
        "words",
        clip=rect,
        sort=True
    )

    lines = {}

    for word in words:
        text = word[4]
        line_number = word[6]

        lines.setdefault(line_number, []).append(word)

    extracted_lines = []

    for line_words in lines.values():
        line_words.sort(key=lambda item: item[0])

        line_text = " ".join(
            word[4] for word in line_words
        )

        extracted_lines.append(line_text)

    return "\n".join(extracted_lines).strip()


def extract_tables(pdf_path, output_path=None):
    """
    Extract scientific tables from PDF files using PyMuPDF.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document = pymupdf.open(pdf_path)

    result = {
        "filename": pdf_path.name,
        "total_pages": len(document),
        "total_tables": 0,
        "pages": []
    }

    try:
        for page_number, page in enumerate(
            document, start=1
        ):

            page_data = {
                "page_number": page_number,
                "table_count": 0,
                "tables": []
            }

            try:
                table_finder = page.find_tables()

                for table_number, table in enumerate(
                    table_finder.tables, start=1
                ):

                    extracted_data = []

                    row_count = len(table.rows)
                    column_count = len(table.rows[0].cells) if row_count else 0

                    for row in table.rows:
                        extracted_row = []

                        for cell in row.cells:
                            cell_text = extract_cell_text(
                                page, cell
                            )

                            extracted_row.append(cell_text)

                        extracted_data.append(extracted_row)

                    table_data = {
                        "table_number": table_number,
                        "row_count": row_count,
                        "column_count": column_count,
                        "data": extracted_data
                    }

                    page_data["tables"].append(table_data)

                page_data["table_count"] = len(
                    page_data["tables"]
                )

            except Exception as error:
                page_data["error"] = str(error)

            result["total_tables"] += page_data["table_count"]
            result["pages"].append(page_data)

    finally:
        document.close()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(
            parents=True, exist_ok=True
        )

        with open(
            output_path, "w", encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

    return result
