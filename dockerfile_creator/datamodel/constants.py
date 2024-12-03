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
        if name == "windows_x86":
            return cls.WINDOWS
        return cls.LINUX


class UpstreamImage(str, Enum):
    """Enumeration for possible upstream images."""

    ROCKYLINUX_8: str = "rockylinux:8"
    CENTOS_7_9: str = "centos:centos7.9.2009"
    CENTOS_7_4: str = "centos:centos7.4.1708"
    WINDOWS_SERVERCORE_LTSC2022: str = (
        "mcr.microsoft.com/windows/servercore:ltsc2022"
    )
    DEBIAN_BOOKWORM: str = "debian:bookworm"


JSON_DATA_SOURCE = (
    "https://raw.githubusercontent.com/gillesvink/"
    "NukeVersionParser/main/nuke-minor-supported-releases.json"
)
"""JSON data to use for fetching new Nuke releases."""


DEVTOOLSETS = {
    16: "gcc-toolset-11",  # probably, as its mentioned in vfx ref
    15: "gcc-toolset-11",
    14: "devtoolset-9",
    13: "devtoolset-6",
    12: "devtoolset-2",
}
"""Matched devtoolset to Nuke major version."""

VISUALSTUDIO_BUILDTOOLS = {
    16: "2022",
    15: "2022",
    14: "2019",
    13: "2017",
    12: "2015",
}
"""Matched Visual Studio build toolset to Nuke major version."""


NUKE_INSTALL_DIRECTORIES: dict[OperatingSystem, str] = {
    OperatingSystem.LINUX: "/usr/local/nuke_install",
    OperatingSystem.WINDOWS: "C:\\\\nuke_install",
}
"""Install directory for Nuke per operating system."""

NUKE_TESTS_DIRECTORIES: dict[OperatingSystem, str] = {
    OperatingSystem.LINUX: "/nuke_tests/",
    OperatingSystem.WINDOWS: "C:\\\\nuke_tests\\",
}
"""Tests directory for Nuke per operating system."""
