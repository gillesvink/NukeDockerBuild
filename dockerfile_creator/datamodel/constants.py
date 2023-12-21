"""Constants file related to Dockerfile builder.

@maintainer: Gilles Vink
"""

from enum import Enum


class InstallCommands(str, Enum):
    """Installation commands as constants."""

    LINUX: str = (
        "RUN \\n"
        "  curl -o /tmp/{filename}.tgz {url}\n"
        "  tar zxvf /tmp/{filename}.tgz\n"
        "  mkdir /usr/local/nuke_install\n"
        "  /tmp/{filename}.run --accept-foundry-eula --prefix=/usr/local/nuke_install --exclude-subdir\n"
    )
