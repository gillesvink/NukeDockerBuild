"""Datamodel to store data related to Dockerfile.

@maintainer: Gilles Vink
"""

import os
from dataclasses import dataclass
from datetime import datetime
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
            IMAGE_COMMANDS.get(self.upstream_image),
            OS_COMMANDS.get(self.operating_system),
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
        label_prefix = "com.nukedockerbuild"
        labels = {
            f"{label_prefix}.version": 1.0,
            f"{label_prefix}.release_date": datetime.now().strftime("%Y-%m-%d"),
            f"{label_prefix}.description": "Ready to use Docker image for building Nuke plugins.",
            f"{label_prefix}.license": "MIT",
            f"{label_prefix}.maintainer": "gilles@vinkvfx.com",
            f"{label_prefix}.source_code": "https://github.com/gillesvink/NukeDockerBuild",
            f"{label_prefix}.based_on": self.upstream_image.value,
            f"{label_prefix}.operating_system": self.operating_system.value,
            f"{label_prefix}.nuke_version": self.nuke_version,
            f"{label_prefix}.nuke_source": self.nuke_source,
        }
        return "\n".join([f"LABEL {key}={value}" for key, value in labels.items()])


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