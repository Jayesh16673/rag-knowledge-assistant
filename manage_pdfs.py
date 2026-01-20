"""
PDF Management Script
Easily add, list, and manage PDF files for the RAG system
Supports any PDF file size
"""

import os
from pathlib import Path
import shutil


DATA_DIR = Path("data")
SAMPLE_DOCS_DIR = DATA_DIR / "sample_docs"


def ensure_directories():
    """Create necessary directories if they don't exist"""
    SAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directory ready: {SAMPLE_DOCS_DIR}")


def list_pdfs():
    """List all PDFs in the data folder"""
    ensure_directories()

    pdfs = list(SAMPLE_DOCS_DIR.glob("*.pdf"))

    if not pdfs:
        print("❌ No PDFs found in", SAMPLE_DOCS_DIR)
        return

    print(f"\n📄 Found {len(pdfs)} PDF(s):\n")
    for i, pdf in enumerate(pdfs, 1):
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"  {i}. {pdf.name} ({size_mb:.2f} MB)")
    print()


def add_pdf(source_path):
    """
    Add a PDF file to the data folder

    Args:
        source_path: Path to the PDF file (can be any size)

    Returns:
        str: Path relative to project root
    """
    ensure_directories()

    source = Path(source_path)

    if not source.exists():
        print(f"❌ File not found: {source_path}")
        return None

    if not source.suffix.lower() == ".pdf":
        print(f"❌ Not a PDF file: {source_path}")
        return None

    # Copy to data folder
    dest = SAMPLE_DOCS_DIR / source.name
    shutil.copy2(source, dest)

    size_mb = dest.stat().st_size / (1024 * 1024)
    print(f"✅ Added: {dest.name} ({size_mb:.2f} MB)")

    relative_path = str(dest).replace("\\", "/")
    print(f"📍 Use in API: {relative_path}")

    return relative_path


def remove_pdf(pdf_name):
    """Remove a PDF file"""
    ensure_directories()

    pdf_path = SAMPLE_DOCS_DIR / pdf_name

    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_name}")
        return False

    pdf_path.unlink()
    print(f"✅ Removed: {pdf_name}")
    return True


def get_pdf_path(pdf_name=None):
    """
    Get the full path to a PDF
    If no name provided, return path to default (sample.pdf)
    """
    ensure_directories()

    if pdf_name is None:
        pdf_name = "sample.pdf"

    pdf_path = SAMPLE_DOCS_DIR / pdf_name
    return str(pdf_path).replace("\\", "/")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        list_pdfs()
    elif sys.argv[1] == "list":
        list_pdfs()
    elif sys.argv[1] == "add" and len(sys.argv) > 2:
        add_pdf(sys.argv[2])
    elif sys.argv[1] == "remove" and len(sys.argv) > 2:
        remove_pdf(sys.argv[2])
    else:
        print("Usage:")
        print("  python manage_pdfs.py list              - List all PDFs")
        print("  python manage_pdfs.py add <path>        - Add a PDF")
        print("  python manage_pdfs.py remove <name>     - Remove a PDF")
