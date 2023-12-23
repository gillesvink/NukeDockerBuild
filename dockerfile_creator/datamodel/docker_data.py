"""Datamodel to store data related to Dockerfile.

@maintainer: Gilles Vink
"""

import os
from dataclasses import dataclass
from itertools import chain
from math import floor
from pathlib import Path

from dockerfile_creator.datamodel.commands import (
    IMAGE_COMMANDS,
    OS_COMMANDS,
    OS_ENVIRONMENTS,
    DockerEnvironments,
)
from dockerfile_creator.datamodel.constants import (
    DEVTOOLSETS,
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
        return "WORKDIR /nuke_build_directory"

    @property
    def run_commands(self) -> str:
        """Return all run commands as a string."""
        commands = chain(
            OS_COMMANDS.get(self.operating_system),
            IMAGE_COMMANDS.get(self.upstream_image),
        )
        formatted_commands = [
            command.to_docker_format() for command in commands
        ]
        formatted_commands = "\n\n".join(formatted_commands)
        if self.operating_system == OperatingSystem.LINUX:
            formatted_commands = formatted_commands.format(
                toolset=DEVTOOLSETS[floor(self.nuke_version)],
                filename=os.path.splitext(os.path.basename(self.nuke_source))[
                    0
                ],
                url=self.nuke_source,
            )
        return formatted_commands

    @property
    def labels(self) -> str:
        """Return image labels as a string."""
        return ""

    @property
    def environments(self) -> str:
        """Return all environments as a string."""
        environments: DockerEnvironments = OS_ENVIRONMENTS[
            self.operating_system
        ]
        return environments.to_docker_format()

    @property
    def upstream_image(self) -> UpstreamImage:
        """Return matching upstream image."""
        if self.nuke_version >= 15.0:
            return UpstreamImage.ROCKYLINUX_8
        if self.nuke_version < 15.0 and self.nuke_version >= 14.0:
            return UpstreamImage.CENTOS_7_9
        return UpstreamImage.CENTOS_7_4

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
            f"{self.labels}\n\n"
            f"{self.run_commands}\n\n"
            f"{self.work_dir}\n\n"
            f"{self.environments}"
        )
