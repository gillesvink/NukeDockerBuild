"""Script that handles the retrieving of data.

@maintainer: Gilles Vink
"""
import json
import os
import re

import requests

from table_retriever.datamodel.constants import GithubData


def _filter_tags(tags: set[str]) -> list[str]:
    """Filter provided tags to keep only the highest versions.

    Args:
        tags: tags to process and remove duplicats.

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


def _retrieve_tags() -> set[str]:
    """Retrieve data from GHCR containing all tags."""
    authorization_header = {"Authorization": f"Bearer {os.environ['TOKEN']}"}
    api_url = f"{GithubData.GHCR_API.value}/tags/list"
    requested_data: requests.Response = requests.get(
        api_url, headers=authorization_header, timeout=3
    )
    if requested_data.status_code != 200:
        msg = "No data found on server."
        raise RetrieveError(msg)

    data = json.loads(requested_data.json())
    tags = data.get("tags")
    return _filter_tags(tags)


class RetrieveError(Exception):
    """Error to raise when something went wrong during retrieving of data."""
