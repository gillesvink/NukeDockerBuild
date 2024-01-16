"""Script that handles collecting of all data.

@maintainer: Gilles Vink
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from table_retriever.worker.data_extractor import manifest_to_docker_image_data
from table_retriever.worker.retriever import (
    retrieve_config_from_manifest,
    retrieve_manifest,
    retrieve_tags,
)

if TYPE_CHECKING:
    from table_retriever.datamodel.table_data import DockerImageData

logger = logging.getLogger(__name__)


def get_all_docker_image_data() -> list[DockerImageData]:
    """Get all docker image data objects."""
    all_tags = retrieve_tags()
    docker_image_data: list[DockerImageData] = []

    for tag in all_tags:
        if "latest" not in tag:
            continue
        manifest = retrieve_manifest(tag)
        config = retrieve_config_from_manifest(manifest)
        docker_image_data.append(
            manifest_to_docker_image_data(
                manifest=manifest, config=config, tag=tag, all_tags=all_tags
            )
        )

        msg = f"Processed '{tag}'"
        logging.info(msg)

    return docker_image_data
