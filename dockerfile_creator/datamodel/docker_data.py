"""Datamodel to store data related to Dockerfile.

@maintainer: Gilles Vink
"""

import os
from dataclasses import dataclass
from math import floor
from pathlib import Path

from dockerfile_creator.datamodel.constants import (
    DEVTOOLSETS,
    SETUP_COMMANDS,
    InstallCommands,
    OperatingSystem,
    UpstreamImage,
)


@dataclass
class Dockerfile:
    """Dataclass to store all data for dockerfile."""

    operating_system: OperatingSystem
    nuke_version: float
    nuke_source: str

    @property
    def upstream_image(self) -> UpstreamImage:
        """Return matching upstream image."""
        if self.nuke_version < 15.0:
            return UpstreamImage.CENTOS_7
        return UpstreamImage.ROCKYLINUX_8

    def get_installation_command(self) -> str:
        """Return the installation command for this dockerfile."""
        filename = os.path.splitext(os.path.basename(self.nuke_source))[0]
        return InstallCommands.LINUX.value.format(
            url=self.nuke_source,
            filename=filename,
        )

    def get_run_command(self) -> str:
        """Return the run command for setting up the image."""
        devtoolset = DEVTOOLSETS[floor(self.nuke_version)]

        return SETUP_COMMANDS[self.upstream_image].format(
            devtoolset=devtoolset
        )

    def get_dockerfile_path(self) -> Path:
        """Return relative path where dockerfile should be written to."""
        return Path(
            f"dockerfiles/{self.nuke_version}/{self.operating_system.value}"
            "/Dockerfile"
        )

    def to_dockerfile(self) -> str:
        """Convert current instance to a dockerfile string."""
        return (
            f"FROM {self.upstream_image.value}\n\n"
            f"{self.get_run_command()}\n"
            f"{self.get_installation_command()}"
        )
