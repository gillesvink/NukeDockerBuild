"""Script that creates the Dockerfiles in their folders.

@maintainer: Gilles Vink
"""
from __future__ import annotations

import copy
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dockerfile_creator.datamodel.docker_data import Dockerfile

logger = logging.getLogger(__name__)


def _keep_only_new_dockerfiles(
    directory: Path, dockerfiles: list[Dockerfile]
) -> None:
    """Check provided dockerfiles if they already exists.

    Args:
        directory: base level directory to start searching.
        dockerfiles: dockerfiles list to modify and check.
    """
    for dockerfile in copy.deepcopy(dockerfiles):
        full_path: Path = directory / dockerfile.get_dockerfile_path()
        if not full_path.is_file():
            continue
        dockerfiles.remove(dockerfile)


def write_dockerfiles(directory: Path, dockerfiles: list[Dockerfile]) -> None:
    """Create dockerfiles from provided directory and dockerfiles.

    Args:
        directory: base level directory to create folders and files.
        dockerfiles: list of dockerfiles to process and create.
    """
    _keep_only_new_dockerfiles(directory, dockerfiles)

    for dockerfile in dockerfiles:
        write_path: Path = directory / dockerfile.get_dockerfile_path()
        write_path.parent.mkdir(parents=True, exist_ok=True)
        write_path.write_text(dockerfile.to_dockerfile())
    msg = f"Created {len(dockerfiles)} new dockerfiles."
    logger.info(msg)
