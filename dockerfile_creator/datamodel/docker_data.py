"""Datamodel to store data related to Dockerfile.

@maintainer: Gilles Vink
"""

from dataclasses import dataclass


class OperatingSystem(str, Enum):
    """Enumeration to store operating system type."""

    WINDOWS: str = "windows"
    MACOS: str = "macos"
    LINUX: str = "linux"


@dataclass
class Dockerfile:
    """Dataclass to store all data for dockerfile."""

    operating_system: OperatingSystem
    nuke_version: float
    nuke_source: str
