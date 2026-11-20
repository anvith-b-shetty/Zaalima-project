import json
from pathlib import Path


def analyze_multimodal_data(figure_json_path, table_json_path, output_path=None):
    """
    Combine figure and table extraction results page by page.
    """

    figure_path = Path(figure_json_path)
    table_path = Path(table_json_path)

    if not figure_path.is_file():
        raise FileNotFoundError(f"Figure JSON not found: {figure_path}")

    if not table_path.is_file():
        raise FileNotFoundError(f"Table JSON not found: {table_path}")

    with figure_path.open("r", encoding="utf-8") as file:
        figure_data = json.load(file)

    with table_path.open("r", encoding="utf-8") as file:
        table_data = json.load(file)

    if figure_data["filename"] != table_data["filename"]:
        raise ValueError("Both extraction files must belong to the same PDF.")

    if figure_data["total_pages"] != table_data["total_pages"]:
        raise ValueError("Page counts do not match.")

    figure_pages = {
        page["page_number"]: page
        for page in figure_data["pages"]
    }

    table_pages = {
        page["page_number"]: page
        for page in table_data["pages"]
    }

    combined_pages = []

    for page_number in range(1, figure_data["total_pages"] + 1):
        figure_page = figure_pages.get(page_number, {})
        table_page = table_pages.get(page_number, {})

        combined_pages.append({
            "page_number": page_number,
            "image_count": figure_page.get("image_count", 0),
            "images": figure_page.get("images", []),
            "table_count": table_page.get("table_count", 0),
            "tables": table_page.get("tables", [])
        })

    result = {
        "filename": figure_data["filename"],
        "total_pages": figure_data["total_pages"],
        "total_images": figure_data["total_images"],
        "total_tables": table_data["total_tables"],
        "pages": combined_pages
    }

    if output_path is None:
        output_path = figure_path.parent / (
            Path(figure_data["filename"]).stem + "_multimodal_analysis.json"
        )
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print("Multimodal analysis completed!")
    print(f"Total pages: {result['total_pages']}")
    print(f"Total images: {result['total_images']}")
    print(f"Total tables: {result['total_tables']}")
    print(f"JSON saved at: {output_path}")

    return result