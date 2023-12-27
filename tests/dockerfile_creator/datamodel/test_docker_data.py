"""Tests related to the Dockerfile datamodel.

@maintainer: Gilles Vink
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dockerfile_creator.datamodel.commands import (
    IMAGE_COMMANDS,
    OS_COMMANDS,
    DockerCommand,
)
from dockerfile_creator.datamodel.docker_data import (
    Dockerfile,
    OperatingSystem,
    UpstreamImage,
)


class TestDockerfile:
    """Tests related to the Dockerfile object."""

    @pytest.fixture()
    def dummy_dockerfile(self) -> Dockerfile:
        """Return a dummy dockerfile."""

        return Dockerfile(
            operating_system=OperatingSystem.LINUX,
            nuke_source=(
                "https://thefoundry.s3.amazonaws.com/products/nuke/"
                "releases/15.0v2/Nuke15.0v2-linux-x86_64.tgz"
            ),
            nuke_version=15.0,
        )

    @pytest.mark.parametrize(
        (
            "test_operating_system",
            "test_nuke_version",
            "expected_upstream_container",
        ),
        [
            (OperatingSystem.LINUX, 15.0, UpstreamImage.ROCKYLINUX_8),
            (OperatingSystem.LINUX, 14.0, UpstreamImage.CENTOS_7_9),
            (OperatingSystem.LINUX, 13.2, UpstreamImage.CENTOS_7_4),
            (OperatingSystem.LINUX, 13.0, UpstreamImage.CENTOS_7_4),
            (OperatingSystem.LINUX, 12.0, UpstreamImage.CENTOS_7_4),
            (
                OperatingSystem.WINDOWS,
                12.0,
                UpstreamImage.WINDOWS_SERVERCORE_LTSC2022,
            ),
        ],
    )
    def test_upstream_image(
        self,
        dummy_dockerfile: Dockerfile,
        test_operating_system: OperatingSystem,
        test_nuke_version: float,
        expected_upstream_container: UpstreamImage,
    ) -> None:
        """Test upstream image to match operating system and nuke version."""
        dummy_dockerfile.operating_system = test_operating_system
        dummy_dockerfile.nuke_version = test_nuke_version

        assert dummy_dockerfile.upstream_image == expected_upstream_container

    @pytest.mark.parametrize(
        ("test_operating_system", "expected_work_dir"),
        [
            (OperatingSystem.LINUX, "WORKDIR /nuke_build_directory"),
            (OperatingSystem.WINDOWS, "WORKDIR C:\\nuke_build_directory"),

        ],
    )
    def test_work_dir(
        self,
        dummy_dockerfile: Dockerfile,
        test_operating_system: OperatingSystem,
        expected_work_dir: str,
    ) -> None:
        """Test to return the correct working dir by operating system."""
        dummy_dockerfile.operating_system = test_operating_system

        assert dummy_dockerfile.work_dir == expected_work_dir

    def test_environments(self, dummy_dockerfile: Dockerfile) -> None:
        """Tests the environments property to call the constants."""
        with patch(
            "dockerfile_creator.datamodel.docker_data.OS_ENVIRONMENTS"
        ) as environments_mock:
            dummy_dockerfile.environments

        environments_mock.__getitem__.assert_called_once_with(
            dummy_dockerfile.operating_system
        )

    def test_run_commands(self) -> None:
        """Test to collect all commands and format them."""
        test_dockerfile = Dockerfile(
            operating_system=OperatingSystem.LINUX,
            nuke_version=15.0,
            nuke_source="https://gillesvink.com/test_file.tgz",
        )
        os_commands_mock = MagicMock(wraps=OS_COMMANDS)
        image_commands_mock = MagicMock(wraps=IMAGE_COMMANDS)

        with patch(
            "dockerfile_creator.datamodel.docker_data.OS_COMMANDS",
            os_commands_mock,
        ) as os_commands_mock, patch(
            "dockerfile_creator.datamodel.docker_data.IMAGE_COMMANDS",
            image_commands_mock,
        ), patch(
            "dockerfile_creator.datamodel.docker_data.Dockerfile._remove_invalid_commands_for_version"
        ) as remove_commands_mock:
            run_commands = test_dockerfile.run_commands

        assert "https://gillesvink.com/test_file.tgz" in run_commands
        os_commands_mock.get.assert_called_once_with(
            test_dockerfile.operating_system, []
        )
        image_commands_mock.get.assert_called_once_with(
            test_dockerfile.upstream_image, []
        )
        remove_commands_mock.assert_called_once()

    @pytest.mark.parametrize(
        ("test_nuke_version", "test_commands", "command_still_in_list"),
        [
            (
                15.0,
                [DockerCommand(commands=["test"])],
                True,
            ),
            (
                15.0,
                [DockerCommand(commands=["test"], minimum_version=15.0)],
                True,
            ),
            (
                15.0,
                [DockerCommand(commands=["test"], minimum_version=16.0)],
                False,
            ),
            (
                15.0,
                [DockerCommand(commands=["test"], maximum_version=15.0)],
                True,
            ),
            (
                15.0,
                [DockerCommand(commands=["test"], maximum_version=14.0)],
                False,
            ),
        ],
    )
    def test_run_commands_depending_version(
        self,
        dummy_dockerfile: Dockerfile,
        test_nuke_version: float,
        test_commands: DockerCommand(),
        command_still_in_list: list[str],
    ) -> None:
        """Test command to be isolated from list if not matching version."""
        dummy_dockerfile.nuke_version = test_nuke_version
        dummy_dockerfile._remove_invalid_commands_for_version(test_commands)

        assert bool(test_commands) == command_still_in_list

    @pytest.mark.parametrize(
        ("test_operating_system", "test_nuke_version", "expected_path"),
        [
            (
                OperatingSystem.LINUX,
                15.0,
                Path("dockerfiles/15.0/linux/Dockerfile"),
            ),
            (
                OperatingSystem.MACOS,
                14.1,
                Path("dockerfiles/14.1/macos/Dockerfile"),
            ),
            (
                OperatingSystem.WINDOWS,
                13.2,
                Path("dockerfiles/13.2/windows/Dockerfile"),
            ),
        ],
    )
    def test_get_dockerfile_path(
        self,
        dummy_dockerfile: Dockerfile,
        test_operating_system: OperatingSystem,
        test_nuke_version: float,
        expected_path: Path,
    ) -> None:
        """Test to return from data object expected path."""
        dummy_dockerfile.operating_system = test_operating_system
        dummy_dockerfile.nuke_version = test_nuke_version

        assert dummy_dockerfile.get_dockerfile_path() == expected_path

    @pytest.mark.parametrize(
        ("test_operating_system", "test_nuke_version"),
        [
            (OperatingSystem.LINUX, 15.0),
            (OperatingSystem.LINUX, 13.0),
        ],
    )
    def test_to_dockerfile(
        self,
        dummy_dockerfile: Dockerfile,
        test_operating_system: OperatingSystem,
        test_nuke_version: float,
    ) -> None:
        """Test calculation of dockerfile string."""
        dummy_dockerfile.operating_system = test_operating_system
        dummy_dockerfile.nuke_version = test_nuke_version

        expected_dockerfile = (
            f"FROM {dummy_dockerfile.upstream_image.value}\n"
            "\n"
            f"{dummy_dockerfile.labels}\n\n"
            f"{dummy_dockerfile.run_commands}\n\n"
            f"{dummy_dockerfile.work_dir}\n\n"
            f"{dummy_dockerfile.environments}"
        )
        assert dummy_dockerfile.to_dockerfile() == expected_dockerfile
