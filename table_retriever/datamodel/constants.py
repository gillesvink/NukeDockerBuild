"""Constants related to the table retriever.

@maintainer: Gilles Vink
"""

from enum import Enum


class GithubData(str, Enum):
    """Data related to Github."""

    REPOSITORY: str = "gillesvink/nukedockerbuild"
    """Repository this table is linked to."""

    GHCR_API: str = f"https://ghcr.io/v2/{REPOSITORY}"
    """API to use for retrieving data."""

    DOCKER_URL: str = f"ghcr.io/{REPOSITORY}"
    """URL that links to the images location."""
