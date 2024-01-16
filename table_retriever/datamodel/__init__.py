"""Datamodel related to the table retriever.

@maintainer: Gilles Vink
"""

from dataclasses import dataclass


@dataclass
class DockerImage:
    """Data that represents a table entry for the image."""

    tag: str
    """Latest tag (recommended to use)"""
    locked_tag: str
    """Tag this latest tag is referencing to."""
    nuke_version: float
    """Nuke version this image is able to compile."""
    target_os: str
    """Operating system this image is targeted to."""
    upstream_image: str
    """Image used to create this image."""
    data_added: str
    """Data image has been created."""
    image_size: float
    """Image size in GB."""
