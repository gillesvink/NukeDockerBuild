"""Script that is responsible for writing and exporting data.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from pathlib import Path
import logging


logger = logging.getLogger(__name__)


def _replace_between_comments(existing_text: str, replace_content: str) -> str:
    """Replace existing text between comments with replace content.

    Args:
        existing_text: existing text to modify
        replace_content: content to add to existing text

    Returns:
        str: replaced content in existing text
    """
    table_start = "<!-- TABLE_START -->"
    table_end = "<!-- TABLE_END -->"

    start_index = existing_text.find(table_start)
    end_index = existing_text.find(table_end)

    if start_index < 0 or end_index < 0:
        msg = "Provided string is not able to find replacement position."
        raise RuntimeError(msg)

    start_index += len(table_start)
    return f"{existing_text[:start_index]}{replace_content}{existing_text[end_index:]}"


def replace_text_in_markdown(path: Path, replace_content: str) -> None:
    """Replace text in markdown with provided content.

    Note:
        This needs to have the README_PATH environment set.

    Args:
        replace_content (str): _description_
    """
    markdown_text = path.read_text(encoding="utf-8")
    markdown_text = _replace_between_comments(markdown_text, replace_content)
    path.write_text(markdown_text, encoding="utf-8")

    msg = f"Updated table in '{path}'"
    logger.info(msg)
