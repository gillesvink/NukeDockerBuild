"""Script that collects Dockerfiles that can be created.

@maintainer: Gilles Vink
"""
import logging
import re

import requests

from dockerfile_creator.datamodel.constants import (
    JSON_DATA_SOURCE,
    OperatingSystem,
)
from dockerfile_creator.datamodel.docker_data import Dockerfile

_VERSION_REGEX = re.compile("^[^v]*")

logger = logging.getLogger(__name__)


def fetch_json_data() -> dict:
    """Fetch data from JSON on Github and return as dict."""
    fetched_data = requests.get(JSON_DATA_SOURCE, timeout=10)
    if fetched_data.status_code != 200:
        msg = "Request returned 404. Please check the URL and try again."
        raise ValueError(msg)
    logger.info("Fetched JSON data containing Nuke releases.")
    return fetched_data.json()


def _nuke_version_to_float(nuke_version: str) -> float:
    """Return Nuke version as a float.

    Args:
        nuke_version: something like 10.0v2

    Returns:
        nuke version as float, for example 10.0
    """
    if "v" not in nuke_version:
        msg = f"Provided data is not a valid version. '{nuke_version}'"
        raise ValueError(msg)
    match = re.search(_VERSION_REGEX, nuke_version)
    return float(match.group())


def get_dockerfiles(data: dict) -> list[Dockerfile]:
    """Convert provided data dict to list of Dockerfile.

    Args:
        data: the requested JSON data.

    Returns:
        list of Dockerfile.
    """
    releases = {
        inner_key: inner_value
        for _, outer_value in data.items()
        for inner_key, inner_value in outer_value.items()
    }

    dockerfiles: list[Dockerfile] = []
    for version, release_data in releases.items():
        installer_data = release_data.get("installer")
        version_number = _nuke_version_to_float(version)

        # FIXME(gillesvink): this is temporarily, as Nuke 12 requires
        # additional work.
        if version_number < 13:
            continue

        for os in ["mac", "linux", "windows"]:
            install_url = installer_data.get(f"{os}_x86")
            if not install_url:
                continue
            dockerfiles.append(
                Dockerfile(
                    operating_system=OperatingSystem.from_shortname(os),
                    nuke_version=version_number,
                    nuke_source=install_url,
                )
            )
    msg = f"Found {len(dockerfiles)} possible dockerfiles."
    logger.info(msg)

    return dockerfiles
