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
    def work_dir(self) -> str:
        """Return the work dir."""
        return "/nuke_build_directory"

    @property
    def run_commands(self) -> str:
        """Return all run commands as a string."""
        return (
            f"{self._get_nuke_installation_command()}\n"
            f"{self._get_setup_command()}"
        )

    @property
    def labels(self) -> str:
        """Return image labels as a string."""
        return ""

    @property
    def environments(self) -> str:
        """Return all environments as a string."""
        return ""

    @property
    def upstream_image(self) -> UpstreamImage:
        """Return matching upstream image."""
        if self.nuke_version < 15.0:
            return UpstreamImage.CENTOS_7
        return UpstreamImage.ROCKYLINUX_8

    @property
    def _nuke_install_directory(self) -> str:
        """Return the nuke install directory."""
        return "/usr/local/nuke_install"

    def _get_nuke_installation_command(self) -> str:
        """Return the installation command for this dockerfile."""
        filename = os.path.splitext(os.path.basename(self.nuke_source))[0]
        return InstallCommands.LINUX.value.format(
            url=self.nuke_source,
            filename=filename,
        )

    def _get_setup_command(self) -> str:
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
            f"{self.labels}\n"
            f"{self.run_commands}\n"
            f"{self.work_dir}\n"
            f"{self.environments}"
        )
