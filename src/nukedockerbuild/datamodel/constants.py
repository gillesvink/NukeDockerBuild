"""Constants file related to Dockerfile builder.

@maintainer: Gilles Vink
"""

from __future__ import annotations

from enum import Enum


class OperatingSystem(str, Enum):
    """Enumeration to store operating system type."""

    WINDOWS: str = "windows"
    LINUX: str = "linux"

    @classmethod
    def from_shortname(cls, shortname: str) -> OperatingSystem:
        """Return enum by provided shortname

        Args:
            shortname: name to get the enum from.

        Raises:
            ValueError: if no matching enum could be found.

        Returns:
            matched enum.
        """
        for os_enum in cls:
            if shortname.lower() in os_enum.value.lower():
                return os_enum
        msg = f"No matching enum for short name: '{shortname}'."
        raise ValueError(msg)

    @classmethod
    def from_mapped_name(cls, name: str) -> OperatingSystem:
        """Return operating system based on mapping for version parser.

        Args:
            name: name to get the enum from.

        Returns:
            matched enum.
        """
        if name == "windows_x86_64":
            return cls.WINDOWS
        return cls.LINUX


class UpstreamImage(str, Enum):
    """Enumeration for possible upstream images."""

    ROCKYLINUX_8: str = "rockylinux:8"
    MANYLINUX_2014: str = "quay.io/pypa/manylinux2014_x86_64"
    DEBIAN_BOOKWORM: str = "debian:bookworm"


JSON_DATA_SOURCE = (
    "https://codeberg.org/gillesvink/NukeVersionParser/"
    "raw/branch/main/nuke-minor-releases.json"
)
"""JSON data to use for fetching new Nuke releases."""


DEVTOOLSETS = {
    16: "11",
    15: "11",
    14: "",
    13: "",
    12: "",
    11: "",
    10: "",
}
"""Matched devtoolset to Nuke major version."""

VISUALSTUDIO_BUILDTOOLS = {
    16: "17",
    15: "17",
    14: "16",
    13: "15",
    12: "15",
}
"""Matched Visual Studio build toolset to Nuke major version."""


NUKE_INSTALL_DIRECTORY: str = "/usr/local/nuke_install"
"""Install directory for Nuke."""

NUKE_TESTS_DIRECTORY: str = "/nuke_tests/"
"""Tests directory for Nuke."""
