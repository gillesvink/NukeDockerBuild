"""Script that handles the data extraction.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from table_retriever.datamodel.table_data import DockerImageData


def _size_calculator(manifest: dict) -> float:
    """Calculate the size in gb for the provided manifest.

    Note: this will be rounded on 1 decimal.

    Args:
        manifest: manifest to process

    Returns:
        float rounded with 1 decimal in Gb.
    """

    layers = manifest.get("layers")
    collected_bytes = 0.0
    for layer in layers:
        collected_bytes += layer.get("size")
    if not collected_bytes:
        msg = "Collected bytes is 0 bytes, which is not possible."
        raise SizeError(msg)
    gigabyte = collected_bytes / (1024 * 1024 * 1024)

    return round(gigabyte, 3)


class SizeError(Exception):
    """Exception to raise when the size does not seem valid."""


def _get_locked_tag(tags: list[str], target_tag: str) -> str:
    """Get locked tag related to the target 'latest' tag."""
    for tag in tags:
        if "latest" in tag:
            continue
        platform, _ = tag.rsplit("-", 1)
        if platform in target_tag:
            return tag
    msg = f"No locked tag found for '{target_tag}'"
    raise TagCollectorError(msg)


class TagCollectorError(Exception):
    """Exception to raise when something goes wrong during tag collecting."""


def manifest_to_docker_image_data(
    manifest: dict, config: dict, tag: str, all_tags: list[str]
) -> DockerImageData:
    """Convert provided manifest into DockerImageData object.

    Args:
        manifest: manifest to read data from and convert
        tag: tag that is being processed.
        all_tags: all available tags.

    Returns:
        DockerImageData: data object containing all data from manifest.
    """
    calculated_size = _size_calculator(manifest)
    locked_tag = _get_locked_tag(tags=all_tags, target_tag=tag)

    labels = config["config"]["Labels"]
    nuke_version = labels["com.nukedockerbuild.nuke_version"]
    nuke_version = float(nuke_version)
    upstream_image = labels["com.nukedockerbuild.based_on"]
    target_os = labels["com.nukedockerbuild.operating_system"]
    date_added = labels["org.opencontainers.image.created"]

    return DockerImageData(
        tag=tag,
        locked_tag=locked_tag,
        nuke_version=nuke_version,
        upstream_image=upstream_image,
        target_os=target_os,
        data_added=date_added,
        image_size=calculated_size,
    )
