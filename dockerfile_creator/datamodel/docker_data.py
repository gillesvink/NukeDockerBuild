"""Datamodel to store data related to Dockerfile.

@maintainer: Gilles Vink
"""

from dataclasses import dataclass


class OperatingSystem(str, Enum):
    """Enumeration to store operating system type."""

    WINDOWS: str = "windows"
    MACOS: str = "macos"
    LINUX: str = "linux"


class UpstreamImage(str, Enum):
    """Enumeration for possible upstream images."""

    ROCKYLINUX_9: str = "rockylinux:9"
    ROCKYLINUX_8: str = "rockylinux:8"
    CENTOS_7: str = "centos:centos7"


@dataclass
class Dockerfile:
    """Dataclass to store all data for dockerfile."""

    operating_system: OperatingSystem
    nuke_version: float
    nuke_source: str
