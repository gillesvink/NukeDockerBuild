"""Datamodel to store data related to Dockerfile.

@maintainer: Gilles Vink
"""

from __future__ import annotations

import os
from copy import copy
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from math import floor

from nukedockerbuild.datamodel.commands import (
    IMAGE_COMMANDS,
    OS_COMMANDS,
    OS_ENVIRONMENTS,
    DockerCommand,
    DockerEnvironments,
)
from nukedockerbuild.datamodel.constants import (
    DEVTOOLSETS,
    NUKE_INSTALL_DIRECTORY,
    VISUALSTUDIO_BUILDTOOLS,
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
        commands = list(
            chain(
                IMAGE_COMMANDS.get(self.upstream_image, []),
                OS_COMMANDS.get(self.operating_system, []),
            )
        )
        self._remove_invalid_commands_for_version(commands)

        formatted_commands = "\n\n".join(
            [command.to_docker_format() for command in commands]
        )

        return formatted_commands.format(
            toolset=self._get_toolset(),
            filename=os.path.splitext(os.path.basename(self.nuke_source))[0],
            url=self.nuke_source,
        )

    @property
    def labels(self) -> str:
        """Return image labels as a string."""
        label_prefix = "org.opencontainers"
        labels = {
            f"{label_prefix}.version": 1.0,
            f"{label_prefix}.image.created": datetime.now().strftime("%Y-%m-%d"),
            f"{label_prefix}.image.description": "Ready to use image for building Nuke plugins.",
            f"{label_prefix}.license": "MIT",
            f"{label_prefix}.url": "https://codeberg.org/gillesvink/NukeDockerBuild",
        }
        label_prefix = "com.nukedockerbuild"
        additional_labels = {
            f"{label_prefix}.based_on": self.upstream_image.value,
            f"{label_prefix}.operating_system": self.operating_system.value,
            f"{label_prefix}.nuke_version": self.nuke_version,
            f"{label_prefix}.nuke_source": self.nuke_source,
        }
        labels.update(additional_labels)
        return "\n".join(
            [
                f"LABEL '{key}'='{value}'"
                if isinstance(value, str)
                else f"LABEL '{key}'={value}"
                for key, value in labels.items()
            ]
        )

    @property
    def args(self) -> str:
        """Return all arguments necessary."""
        all_args = ["NUKE_SOURCE_FILES"]
        if self.operating_system == OperatingSystem.WINDOWS:
            all_args.append("TOOLCHAIN")
        return "\n".join(f"ARG {argument}" for argument in all_args)

    @property
    def copy(self) -> str:
        """Additional copy statements to include."""
        nuke_sources = f"COPY $NUKE_SOURCE_FILES {NUKE_INSTALL_DIRECTORY}"
        if self.operating_system == OperatingSystem.WINDOWS:
            return f"{nuke_sources}\nCOPY $TOOLCHAIN /nukedockerbuild/"
        return f"{nuke_sources}"

    @property
    def environments(self) -> str:
        """Return all environments as a string."""
        os_environments: DockerEnvironments = OS_ENVIRONMENTS[self.operating_system]
        general_environments = DockerEnvironments({"NUKE_VERSION": self.nuke_version})

        return "\n".join(
            environments.to_docker_format().format(cpp_version=self.cpp_version)
            for environments in [os_environments, general_environments]
        )

    @property
    def cpp_version(self) -> int:
        matched_cpp_version = {
            16: 17,
            15: 17,
            14: 17,
            13: 14,
            12: 14,
            11: 11,
            10: 11,
        }

        return matched_cpp_version[int(self.nuke_version)]

    @property
    def upstream_image(self) -> UpstreamImage:
        """Return matching upstream image."""
        if self.operating_system == OperatingSystem.WINDOWS:
            return UpstreamImage.DEBIAN_BOOKWORM
        if self.nuke_version < 15.0:
            return UpstreamImage.MANYLINUX_2014
        return UpstreamImage.ROCKYLINUX_8

    def to_dockerfile(self) -> str:
        """Convert current instance to a dockerfile string."""
        return (
            f"FROM {self.upstream_image.value}\n\n"
            f"{self.labels}\n\n"
            f"{self.args}\n\n"
            f"{self.copy}\n\n"
            f"{self.run_commands}\n\n"
            f"{self.work_dir}\n\n"
            f"{self.environments}"
        )

    def _get_toolset(self) -> str:
        """Return the toolset needed for this Dockerfile."""
        if self.operating_system == OperatingSystem.WINDOWS:
            return VISUALSTUDIO_BUILDTOOLS[floor(self.nuke_version)]
        return DEVTOOLSETS[floor(self.nuke_version)]

    def _remove_invalid_commands_for_version(
        self, commands: list[DockerCommand]
    ) -> None:
        """Remove invalid commands for the Nuke Version.

        This checks if the command has a min and max version specified.

        Args:
            commands: commands to check for Nuke version requirements
        """
        for command in copy(commands):
            if (
                command.maximum_version is not None
                and command.maximum_version < self.nuke_version
            ):
                commands.remove(command)
            if (
                command.minimum_version is not None
                and command.minimum_version > self.nuke_version
            ):
                commands.remove(command)
