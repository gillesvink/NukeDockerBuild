"""Script that executes the dockerfile creator.

@maintainer: Gilles Vink
"""

import logging
import os
from pathlib import Path

from dockerfile_creator.creator.collector import (
    fetch_json_data,
    get_dockerfiles,
)
from dockerfile_creator.creator.create_dockerfiles import write_dockerfiles

FORMAT = "[%(asctime)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)


def generate_dockerfiles() -> None:
    """Generate dockerfiles in directory.

    Note:
        make sure to set the DOCKERFILES_DIRECTORY env.
    """
    dockerfiles_directory = os.getenv("DOCKERFILES_DIRECTORY")
    if not dockerfiles_directory:
        msg = "DOCKERFILES_DIRECTORY environment not set. Cannot create dockerfiles."
        raise ValueError(msg)

    json_data = fetch_json_data()
    dockerfiles = get_dockerfiles(data=json_data)
    write_dockerfiles(
        directory=Path(dockerfiles_directory), dockerfiles=dockerfiles
    )


if __name__ == "__main__":
    generate_dockerfiles()
