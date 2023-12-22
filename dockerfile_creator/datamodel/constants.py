"""Constants file related to Dockerfile builder.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from enum import Enum

JSON_DATA_SOURCE = (
    "https://raw.githubusercontent.com/gillesvink/"
    "NukeVersionParser/main/nuke-minor-supported-releases.json"
)
"""JSON data to use for fetching new Nuke releases."""


class InstallCommands(str, Enum):
    """Installation commands as constants."""

    LINUX: str = (
        "RUN curl -o /tmp/{filename}.tgz {url} \\ \n"
        "  && tar zxvf /tmp/{filename}.tgz -C /tmp/ \\ \n"
        "  && mkdir /usr/local/nuke_install \\ \n"
        "  && /tmp/{filename}.run --accept-foundry-eula "
        "--prefix=/usr/local/nuke_install --exclude-subdir \\ \n"
        "  && rm -rf /tmp/* \\ \n"
        "  && cp -r /usr/local/nuke_install/Documentation/NDKExamples/"
        "examples/ /nuke_tests/ \\ \n"
        "  && rm -rf nukeCrashFeedback plugins configs Resources "
        "resources lib pythonextensions translations bin "
        "Documentation libtorch* libcudnn* libcublas* "
        "libcusparse* libcusolver* libmkl* \\ \n"
    )


class OperatingSystem(str, Enum):
    """Enumeration to store operating system type."""

    WINDOWS: str = "windows"
    MACOS: str = "macos"
    LINUX: str = "linux"

    @classmethod
    def from_shortname(cls, shortname: str) -> OperatingSystem:
        """Return enum by provided shortname"""
        for os_enum in cls:
            if shortname.lower() in os_enum.name.lower():
                return os_enum
        msg = f"No matching enum for short name: {shortname}"
        raise ValueError(msg)


class UpstreamImage(str, Enum):
    """Enumeration for possible upstream images."""

    ROCKYLINUX_8: str = "rockylinux:8"
    CENTOS_7: str = "centos:centos7"


DEVTOOLSETS = {
    15: "gcc-toolset-11",
    14: "devtoolset-9",
    13: "devtoolset-6",
}
"""Matched devtoolset to Nuke major version."""

SETUP_COMMANDS: dict = {
    UpstreamImage.ROCKYLINUX_8: (
        "RUN dnf install {devtoolset} -y \\ \n"
        "  && dnf install cmake3 -y \\ \n"
        "  && dnf install mesa-libGLU-devel -y \\ \n"
        "  && echo 'unset BASH_ENV PROMPT_COMMAND ENV && source "
        "scl_source enable gcc-toolset-11' >> /usr/bin/scl_enable"
    ),
    UpstreamImage.CENTOS_7: (
        "RUN yum install {devtoolset} -y \\ \n"
        "  && yum install cmake3 -y \\ \n"
        "  && scl_source enable {devtoolset}"
    ),
}
"""Setup commands matched to their image."""
