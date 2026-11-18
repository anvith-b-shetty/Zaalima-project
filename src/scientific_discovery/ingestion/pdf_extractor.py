
import pymupdf
import json
from pathlib import Path


def extract_pdf_text(pdf_path):
    """Extract scientific PDF text, metadata and page information."""

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Please provide a PDF file.")

    extracted_data = {
        "filename": pdf_path.name,
        "metadata": {},
        "total_pages": 0,
        "pages": []
    }

    with pymupdf.open(pdf_path) as document:

        extracted_data["metadata"] = document.metadata
        extracted_data["total_pages"] = len(document)

        for page_number, page in enumerate(document, start=1):

            page_text = page.get_text("text").strip()

            extracted_data["pages"].append({
                "page_number": page_number,
                "text": page_text,
                "is_empty": not bool(page_text)
            })

    output_path = pdf_path.with_name(
        pdf_path.stem + "_extracted.json"
    )

    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(
            extracted_data,
            json_file,
            indent=4,
            ensure_ascii=False
        )

    print("PDF extraction completed!")
    print(f"Total pages: {extracted_data['total_pages']}")
    print(f"JSON saved at: {output_path}")

    return extracted_data
