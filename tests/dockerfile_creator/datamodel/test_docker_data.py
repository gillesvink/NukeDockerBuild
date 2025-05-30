"""Tests related to the Dockerfile datamodel.

@maintainer: Gilles Vink
"""

from unittest.mock import MagicMock, patch

import pytest

from nukedockerbuild.datamodel.commands import (
    IMAGE_COMMANDS,
    OS_COMMANDS,
    DockerCommand,
    DockerEnvironments,
)
from nukedockerbuild.datamodel.docker_data import (
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
            (OperatingSystem.LINUX, 14.0, UpstreamImage.MANYLINUX_2014),
            (OperatingSystem.LINUX, 13.2, UpstreamImage.MANYLINUX_2014),
            (OperatingSystem.LINUX, 13.0, UpstreamImage.MANYLINUX_2014),
            (OperatingSystem.LINUX, 12.0, UpstreamImage.MANYLINUX_2014),
            (OperatingSystem.LINUX, 11.0, UpstreamImage.MANYLINUX_2014),
            (OperatingSystem.LINUX, 10.0, UpstreamImage.MANYLINUX_2014),
            (
                OperatingSystem.WINDOWS,
                15.0,
                UpstreamImage.DEBIAN_BOOKWORM,
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
        ("test_operating_system", "test_version", "expected_toolset"),
        [
            (OperatingSystem.LINUX, 15.0, "11"),
            (OperatingSystem.LINUX, 15.1, "11"),
            (OperatingSystem.WINDOWS, 15.0, "17"),
            (OperatingSystem.WINDOWS, 15.1, "17"),
            (OperatingSystem.WINDOWS, 14.9, "16"),
            (OperatingSystem.WINDOWS, 13.0, "15"),
            (OperatingSystem.WINDOWS, 12.0, "15"),
        ],
    )
    def test__get_toolset(
        self,
        dummy_dockerfile: Dockerfile,
        test_operating_system: str,
        test_version: float,
        expected_toolset: str,
    ) -> None:
        """Test to return the expected toolset by version and os."""
        dummy_dockerfile.operating_system = test_operating_system
        dummy_dockerfile.nuke_version = test_version
        assert dummy_dockerfile._get_toolset() == expected_toolset

    @pytest.mark.parametrize(
        ("test_operating_system", "expected_work_dir"),
        [
            (OperatingSystem.LINUX, "WORKDIR /nuke_build_directory"),
            (OperatingSystem.WINDOWS, "WORKDIR /nuke_build_directory"),
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
        os_environments_mock = MagicMock(spec=dict)
        os_environments_mock.__getitem__.return_value = DockerEnvironments(
            {"test": "test"}
        )
        with patch(
            "nukedockerbuild.datamodel.docker_data.OS_ENVIRONMENTS",
            os_environments_mock,
        ) as environments_mock:
            collected_environments = dummy_dockerfile.environments

        environments_mock.__getitem__.assert_called_once_with(
            dummy_dockerfile.operating_system
        )
        assert f"NUKE_VERSION={dummy_dockerfile.nuke_version}" in collected_environments

    @pytest.mark.parametrize(
        ("test_operating_system", "test_nuke_version", "test_nuke_source"),
        [
            (OperatingSystem.LINUX, 15.0, "hello"),
            (OperatingSystem.LINUX, 13.0, "github.com"),
        ],
    )
    def test_labels(
        self,
        dummy_dockerfile: Dockerfile,
        test_operating_system: OperatingSystem,
        test_nuke_version: float,
        test_nuke_source: str,
    ) -> None:
        """Test to return the necessary labels to be returned."""
        dummy_dockerfile.operating_system = test_operating_system
        dummy_dockerfile.nuke_version = test_nuke_version
        dummy_dockerfile.nuke_source = test_nuke_source

        retrieved_labels = dummy_dockerfile.labels

        assert (
            f"LABEL 'com.nukedockerbuild.nuke_version'={test_nuke_version}"
            in retrieved_labels
        )
        assert "LABEL 'org.opencontainers.version'=" in retrieved_labels
        assert (
            f"LABEL 'com.nukedockerbuild.operating_system'='{test_operating_system.value}'"
            in retrieved_labels
        )
        assert (
            f"LABEL 'com.nukedockerbuild.nuke_source'='{test_nuke_source}'"
            in retrieved_labels
        )

    @pytest.mark.parametrize(
        "os",
        [
            OperatingSystem.LINUX,
            OperatingSystem.WINDOWS,
        ],
    )
    def test_run_commands(self, os: OperatingSystem) -> None:
        """Test to collect all commands and format them."""
        test_dockerfile = Dockerfile(
            operating_system=os,
            nuke_version=15.0,
            nuke_source="https://gillesvink.com/test_file.tgz",
        )
        os_commands_mock = MagicMock(wraps=OS_COMMANDS)
        image_commands_mock = MagicMock(wraps=IMAGE_COMMANDS)

        with (
            patch(
                "nukedockerbuild.datamodel.docker_data.OS_COMMANDS",
                os_commands_mock,
            ) as os_commands_mock,
            patch(
                "nukedockerbuild.datamodel.docker_data.IMAGE_COMMANDS",
                image_commands_mock,
            ),
            patch(
                "nukedockerbuild.datamodel.docker_data.Dockerfile."
                "_remove_invalid_commands_for_version"
            ) as remove_commands_mock,
        ):
            test_dockerfile.run_commands

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
        test_commands: DockerCommand([]),
        command_still_in_list: list[str],
    ) -> None:
        """Test command to be isolated from list if not matching version."""
        dummy_dockerfile.nuke_version = test_nuke_version
        dummy_dockerfile._remove_invalid_commands_for_version(test_commands)

        assert bool(test_commands) == command_still_in_list

    @pytest.mark.parametrize(
        ("test_operating_system", "expected_result"),
        [
            (
                OperatingSystem.LINUX,
                "ARG NUKE_SOURCE_FILES",
            ),
            (
                OperatingSystem.WINDOWS,
                "ARG NUKE_SOURCE_FILES\nARG TOOLCHAIN",
            ),
        ],
    )
    def test_args(
        self,
        dummy_dockerfile: Dockerfile,
        test_operating_system: OperatingSystem,
        expected_result: str,
    ) -> None:
        """Test args return source files and possibly toolchain."""
        dummy_dockerfile.operating_system = test_operating_system

        assert dummy_dockerfile.args == expected_result

    @pytest.mark.parametrize(
        ("test_operating_system", "expected_result"),
        [
            (
                OperatingSystem.LINUX,
                "COPY $NUKE_SOURCE_FILES /usr/local/nuke_install",
            ),
            (
                OperatingSystem.WINDOWS,
                "COPY $NUKE_SOURCE_FILES /usr/local/nuke_install\nCOPY $TOOLCHAIN /nukedockerbuild/",
            ),
        ],
    )
    def test_copy(
        self,
        dummy_dockerfile: Dockerfile,
        test_operating_system: OperatingSystem,
        expected_result: str,
    ) -> None:
        """Test copy to only return expected copy statements."""
        dummy_dockerfile.operating_system = test_operating_system
        assert dummy_dockerfile.copy == expected_result

    @pytest.mark.parametrize(
        ("test_operating_system", "test_nuke_version"),
        [
            (OperatingSystem.LINUX, 15.0),
            (OperatingSystem.LINUX, 13.0),
            (OperatingSystem.WINDOWS, 13.0),
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
            f"{dummy_dockerfile.args}\n\n"
            f"{dummy_dockerfile.copy}\n\n"
            f"{dummy_dockerfile.run_commands}\n\n"
            f"{dummy_dockerfile.work_dir}\n\n"
            f"{dummy_dockerfile.environments}"
        )
        assert dummy_dockerfile.to_dockerfile() == expected_dockerfile
