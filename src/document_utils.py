#!/usr/bin/env python3
"""
Document Conversion Utilities
Provides functions to convert PDF and Word documents to Markdown format
"""

import os
from pathlib import Path
from typing import Optional


def document_path_to_markdown(file_path: str) -> str:
    """
    Convert a PDF or Word document to Markdown format.

    Args:
        file_path: Path to the PDF (.pdf) or Word (.docx) document

    Returns:
        str: The document content converted to Markdown format

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file type is not supported
    """
    # Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get file extension
    file_ext = Path(file_path).suffix.lower()

    # Route to appropriate converter based on file type
    if file_ext == '.pdf':
        return _convert_pdf_to_markdown(file_path)
    elif file_ext == '.docx':
        return _convert_docx_to_markdown(file_path)
    else:
        raise ValueError(
            f"Unsupported file format: {file_ext}. "
            f"Supported formats are: .pdf, .docx"
        )


def _convert_pdf_to_markdown(pdf_path: str) -> str:
    """
    Convert PDF file to Markdown.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        str: Markdown-formatted text extracted from PDF
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError(
            "pdfplumber is required for PDF conversion. "
            "Install it with: pip install pdfplumber"
        )

    markdown_content = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract text from page
            text = page.extract_text()

            if text:
                # Add page separator for multi-page documents
                if page_num > 1:
                    markdown_content.append("\n---\n")

                # Clean up the text
                text = text.strip()
                markdown_content.append(text)

    # Join all pages
    result = "\n\n".join(markdown_content)

    return result if result else ""


def _convert_docx_to_markdown(docx_path: str) -> str:
    """
    Convert Word document to Markdown.

    Args:
        docx_path: Path to the .docx file

    Returns:
        str: Markdown-formatted text extracted from Word document
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError(
            "python-docx is required for Word document conversion. "
            "Install it with: pip install python-docx"
        )

    doc = Document(docx_path)
    markdown_content = []

    for para in doc.paragraphs:
        text = para.text.strip()

        if not text:
            continue

        # Convert heading styles to Markdown headers
        if para.style.name.startswith('Heading'):
            # Extract heading level (e.g., 'Heading 1' -> 1)
            try:
                level = int(para.style.name.split()[-1])
                markdown_content.append(f"{'#' * level} {text}")
            except (ValueError, IndexError):
                # If we can't parse the heading level, treat as regular heading
                markdown_content.append(f"# {text}")
        else:
            # Regular paragraph
            markdown_content.append(text)

    # Join all paragraphs
    result = "\n\n".join(markdown_content)

    return result if result else ""


def binary_document_to_markdown(binary_data: bytes, file_extension: str) -> str:
    """
    Convert binary document data to Markdown format.

    Args:
        binary_data: Binary content of the document
        file_extension: File extension (.pdf or .docx)

    Returns:
        str: The document content converted to Markdown format

    Raises:
        ValueError: If the file type is not supported
    """
    import tempfile

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp_file:
        tmp_file.write(binary_data)
        tmp_path = tmp_file.name

    try:
        # Use the main conversion function
        result = document_path_to_markdown(tmp_path)
        return result
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
