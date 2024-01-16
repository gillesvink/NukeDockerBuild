"""Converter script that converts provided DockerImageData into markdown."""

from __future__ import annotations

import logging
import operator
from copy import copy
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from table_retriever.datamodel.table_data import DockerImageData

logger = logging.getLogger(__name__)


def _sort_docker_image_data(docker_data: list[DockerImageData]) -> None:
    """Sort provided data by Nuke version and then tag name.

    Args:
        docker_data: sort provided data
    """

    docker_data.sort(key=operator.attrgetter("tag"))
    docker_data.sort(key=operator.attrgetter("nuke_version"), reverse=True)


def _convert_data_to_dataframe(
    docker_data: list[DockerImageData],
) -> pd.DataFrame:
    """Convert provided DockerImageData into a Pandas DataFrame."""
    data = {
        "Tag": [],
        "Locked Tag": [],
        "Nuke Version": [],
        "OS": [],
        "Upstream Image": [],
        "Date Added": [],
        "Image Size (GB)": [],
    }

    for image_data in docker_data:
        data["Tag"].append(image_data.tag)
        data["Locked Tag"].append(image_data.locked_tag)
        data["Nuke Version"].append(image_data.nuke_version)
        data["OS"].append(image_data.target_os)
        data["Upstream Image"].append(image_data.upstream_image)
        data["Date Added"].append(image_data.data_added)
        data["Image Size (GB)"].append(image_data.image_size)

    return pd.DataFrame(data)


def convert_and_sort_data_to_markdown(
    docker_data: list[DockerImageData],
) -> str:
    """Convert and sort data into a markdown format.

    Args:
        docker_data: docker data to convert.

    Returns:
        markdown table of docker data.
    """
    data = copy(docker_data)
    _sort_docker_image_data(data)
    dataframe = _convert_data_to_dataframe(data)
    markdown = dataframe.to_markdown(index=False, floatfmt=(".1f", ".1f", ".1f"))

    msg = f"Created markdown: \n {markdown}"
    logging.info(msg)

    return f"\n{markdown}\n"
