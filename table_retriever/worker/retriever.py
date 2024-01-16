"""Script that handles the retrieving of data.

@maintainer: Gilles Vink
"""
from __future__ import annotations

import logging
import re
from functools import lru_cache

import requests

from table_retriever.datamodel.constants import GithubData

TIMEOUT: int = 10
"""General timeout for requests."""

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_header() -> dict[str]:
    """Get header to send to requests including a token."""
    response = requests.get(
        url=f"https://ghcr.io/token?scope=repository:{GithubData.REPOSITORY.value}:pull",
        timeout=TIMEOUT,
    )
    token = response.json()
    token = token.get("token")
    if not token:
        msg = "No token has provided."
        raise RetrieveError(msg)
    return {"Authorization": f"Bearer {token}"}


def _filter_tags(tags: set[str]) -> list[str]:
    """Filter provided tags to keep only the highest versions.

    Args:
        tags: tags to process and remove duplicates.

    Returns:
        filtered list of tags.
    """
    collected_tags = set()
    for tag in tags:
        if "latest" in tag:
            collected_tags.add(tag)

        platform, _ = tag.rsplit("-", 1)
        if not any(
            platform in collected_tag for collected_tag in collected_tags
        ):
            collected_tags.add(tag)

        regex_match = rf"{platform}-((\d).(\d))"
        same_target_tags = [tag for tag in tags if re.match(regex_match, tag)]
        same_target_tags.sort(reverse=True)
        if same_target_tags[0] != tag:
            continue

        collected_tags.add(tag)

    return collected_tags


def _get_requested_data(url: str) -> requests.Response:
    """Get requested data if found.

    Args:
        url: url to get data from.

    Raises:
        RetrieveError: if data could not be found.

    Returns:
        Response object containing retrieved data.
    """
    requested_data: requests.Response = requests.get(
        url=url, headers=_get_header(), timeout=TIMEOUT
    )
    if requested_data.status_code != 200:
        msg = f"No data found on server: '{requested_data}'"
        raise RetrieveError(msg)
    return requested_data


def retrieve_tags() -> set[str]:
    """Retrieve data from GHCR containing all tags."""
    api_url = f"{GithubData.GHCR_API.value}/tags/list"
    requested_data = _get_requested_data(url=api_url)
    data = requested_data.json()
    tags = data.get("tags")

    collected_tags = _filter_tags(tags)

    msg = f"Collected tags: '{collected_tags}'"
    logger.info(msg)

    return collected_tags


def retrieve_manifest(tag: str) -> dict:
    """Retrieve manifests for a specific tag.

    Args:
        tag: tag to get data from.
    """
    api_url = f"{GithubData.GHCR_API.value}/manifests/{tag}"
    requested_data = _get_requested_data(url=api_url)
    return requested_data.json()


def retrieve_config_from_manifest(manifest: dict) -> dict:
    """Return collected config from provided manifest.

    Args:
        manifest: manifest that includes the digest data.

    Returns:
        dict: containing config data.
    """
    digest = manifest["config"]["digest"]
    api_url = f"{GithubData.GHCR_API.value}/blobs/{digest}"
    requested_data = _get_requested_data(url=api_url)
    return requested_data.json()


class RetrieveError(Exception):
    """Error to raise when something went wrong during retrieving of data."""
