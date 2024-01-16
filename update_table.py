"""Script that handles the updating of the README.md.

@maintainer: Gilles Vink
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from table_retriever.worker.converter import convert_and_sort_data_to_markdown
from table_retriever.worker.data_collector import get_all_docker_image_data
from table_retriever.worker.exporter import replace_text_in_markdown

FORMAT = "[%(asctime)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)


def update_table() -> None:
    """Function that handles updating of the provided file."""
    readme_path = os.getenv("README_PATH")
    if not readme_path:
        msg = "README_PATH environment has not been set."
        raise ValueError(msg)

    path = Path(readme_path)
    docker_data = get_all_docker_image_data()
    markdown = convert_and_sort_data_to_markdown(docker_data)
    replace_text_in_markdown(path, markdown)


if __name__ == "__main__":
    update_table()
