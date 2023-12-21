"""Tests related to the Dockerfile datamodel.

@maintainer: Gilles Vink
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from dockerfile_creator.datamodel.constants import (
    InstallCommands,
    SETUP_COMMANDS,
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
            nuke_source="https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.0v2/Nuke15.0v2-linux-x86_64.tgz",
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
            (OperatingSystem.LINUX, 14.0, UpstreamImage.CENTOS_7),
            (OperatingSystem.LINUX, 13.2, UpstreamImage.CENTOS_7),
            (OperatingSystem.LINUX, 13.0, UpstreamImage.CENTOS_7),
            (OperatingSystem.LINUX, 12.0, UpstreamImage.CENTOS_7),
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
        (
            "test_upstream_image",
            "test_url",
            "expected_installation_command",
        ),
        [
            (
                UpstreamImage.ROCKYLINUX_8,
                "https://my/test/nuke_installation_file.tgz",
                InstallCommands.LINUX.value.format(
                    url="https://my/test/nuke_installation_file.tgz",
                    filename="nuke_installation_file",
                ),
            ),
            (
                UpstreamImage.CENTOS_7,
                "https://my/test/nuke_installation_file.tgz",
                InstallCommands.LINUX.value.format(
                    url="https://my/test/nuke_installation_file.tgz",
                    filename="nuke_installation_file",
                ),
            ),
        ],
    )
    def test_get_installation_command(
        self,
        dummy_dockerfile: Dockerfile,
        test_upstream_image: UpstreamImage,
        test_url: str,
        expected_installation_command: str,
    ) -> None:
        """Test the calculation of the installation command."""
        dummy_dockerfile.nuke_source = test_url
        with patch(
            "dockerfile_creator.datamodel.docker_data.Dockerfile.upstream_image",
            test_upstream_image,
        ):
            assert (
                dummy_dockerfile.get_installation_command()
                == expected_installation_command
            )

    @pytest.mark.parametrize(
        ("test_upstream_image", "test_nuke_version", "expected_run_command"),
        [
            (
                UpstreamImage.ROCKYLINUX_8,
                15.0,
                SETUP_COMMANDS[UpstreamImage.ROCKYLINUX_8].format(devtoolset="gcc-toolset-11"),
            ),
            (
                UpstreamImage.CENTOS_7,
                14.0,
                SETUP_COMMANDS[UpstreamImage.CENTOS_7].format(devtoolset="devtoolset-9"),
            ),
            (
                UpstreamImage.CENTOS_7,
                13.0,
                SETUP_COMMANDS[UpstreamImage.CENTOS_7].format(devtoolset="devtoolset-6"),
            ),
        ],
    )
    def test_get_run_command(
        self,
        dummy_dockerfile: Dockerfile,
        test_upstream_image: UpstreamImage,
        test_nuke_version: float,
        expected_run_command: str,
    ) -> None:
        """Test the calculation of the run command and follow vfx reference."""
        dummy_dockerfile.nuke_version = test_nuke_version
        with patch(
            "dockerfile_creator.datamodel.docker_data.Dockerfile.upstream_image",
            test_upstream_image,
        ):
            assert dummy_dockerfile.get_run_command() == expected_run_command

    @pytest.mark.xfail()
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
                Path("dockerfiles/14.0/macos/Dockerfile"),
            ),
            (
                OperatingSystem.WINDOWS,
                13.2,
                Path("dockerfiles/14.0/windows/Dockerfile"),
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

    @pytest.mark.xfail()
    @pytest.mark.parametrize(
        ("test_operating_system", "test_nuke_version"),
        [
            (OperatingSystem.LINUX, 15.0),
            (OperatingSystem.LINUX, 13.0),
            (OperatingSystem.MACOS, 15.0),
            (OperatingSystem.WINDOWS, 15.0),
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
            "# Auto generated Dockerfile for Nuke compiling\n"
            f"FROM {dummy_dockerfile.upstream_image}\n"
            "\n"
            f"RUN {dummy_dockerfile.get_run_command()}\n"
            f"RUN {dummy_dockerfile.get_installation_command()}"
        )

        assert dummy_dockerfile.to_dockerfile() == expected_dockerfile
