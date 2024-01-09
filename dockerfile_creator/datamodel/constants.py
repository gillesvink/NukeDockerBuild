"""Constants file related to Dockerfile builder.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from enum import Enum


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
        msg = f"No matching enum for short name: '{shortname}'."
        raise ValueError(msg)


class UpstreamImage(str, Enum):
    """Enumeration for possible upstream images."""

    ROCKYLINUX_8: str = "rockylinux:8"
    CENTOS_7_9: str = "centos:centos7.9.2009"
    CENTOS_7_4: str = "centos:centos7.4.1708"
    WINDOWS_SERVERCORE_LTSC2022: str = (
        "mcr.microsoft.com/windows/servercore:ltsc2022"
    )


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
    OperatingSystem.WINDOWS: "C:\\nuke_install",
}
"""Install directory for Nuke per operating system."""

NUKE_TESTS_DIRECTORIES: dict[OperatingSystem, str] = {
    OperatingSystem.LINUX: "/nuke_tests/",
    OperatingSystem.WINDOWS: "C:\\\\nuke_tests\\",
}
"""Tests directory for Nuke per operating system."""

KEEP_SOURCE_FILES: list = ["tests", "cmake", "include", "source", "*Fdk*"]
"""Files that should be kept for compiling purposes."""
