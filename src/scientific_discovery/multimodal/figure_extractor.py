
import pymupdf
import json
from pathlib import Path


def extract_pdf_images(pdf_path, output_dir=None):
    """
    Extract embedded images from a scientific PDF.

    Records:
    - PDF filename and metadata
    - Page numbers
    - Image filenames
    - Image dimensions
    - Image formats
    - Total extracted images
    """

    pdf_path = Path(pdf_path)

    # Validate PDF file
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not pdf_path.is_file():
        raise ValueError("The provided path is not a file.")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Please provide a PDF file.")

    # Set output directory
    if output_dir is None:
        output_dir = pdf_path.with_name(
            pdf_path.stem + "_images"
        )
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    extracted_data = {
        "filename": pdf_path.name,
        "metadata": {},
        "total_pages": 0,
        "total_images": 0,
        "output_directory": str(output_dir),
        "pages": []
    }

    with pymupdf.open(pdf_path) as document:

        extracted_data["metadata"] = document.metadata
        extracted_data["total_pages"] = len(document)

        for page_number, page in enumerate(document, start=1):

            page_images = []
            seen_xrefs = set()

            # Get embedded images from the page
            images = page.get_images(full=True)

            for image_number, image in enumerate(images, start=1):

                xref = image[0]

                # Skip duplicate references on the same page
                if xref in seen_xrefs:
                    continue

                seen_xrefs.add(xref)

                try:
                    image_info = document.extract_image(xref)

                    image_bytes = image_info["image"]
                    image_extension = image_info.get("ext", "bin")

                    image_filename = (
                        f"page_{page_number:03d}_"
                        f"image_{image_number:03d}."
                        f"{image_extension}"
                    )

                    image_path = output_dir / image_filename

                    # Save extracted image
                    image_path.write_bytes(image_bytes)

                    image_record = {
                        "image_number": image_number,
                        "xref": xref,
                        "filename": image_filename,
                        "format": image_extension,
                        "width": image_info.get("width"),
                        "height": image_info.get("height"),
                        "size_bytes": len(image_bytes)
                    }

                    page_images.append(image_record)

                except Exception as error:
                    page_images.append({
                        "image_number": image_number,
                        "xref": xref,
                        "error": str(error)
                    })

            extracted_data["pages"].append({
                "page_number": page_number,
                "image_count": sum(
                    1 for item in page_images
                    if "filename" in item
                ),
                "images": page_images,
                "is_empty": len(page_images) == 0
            })

    extracted_data["total_images"] = sum(
        page["image_count"]
        for page in extracted_data["pages"]
    )

    # Save extraction results as JSON
    json_path = pdf_path.with_name(
        pdf_path.stem + "_images_extracted.json"
    )

    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(
            extracted_data,
            json_file,
            indent=4,
            ensure_ascii=False
        )

    print("PDF image extraction completed!")
    print(f"Total pages: {extracted_data['total_pages']}")
    print(f"Total images: {extracted_data['total_images']}")
    print(f"Images saved in: {output_dir}")
    print(f"JSON saved at: {json_path}")

    return extracted_data
