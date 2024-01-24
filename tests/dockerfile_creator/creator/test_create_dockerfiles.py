"""Tests for the script that creates the dockerfiles."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dockerfile_creator.creator.create_dockerfiles import (
    _get_dockerfile_path,
    _keep_only_new_dockerfiles,
    write_dockerfiles,
)
from dockerfile_creator.datamodel.constants import OperatingSystem
from dockerfile_creator.datamodel.docker_data import Dockerfile


def test__keep_only_new_dockerfiles(tmp_path: Path) -> None:
    """Test to remove any dockerfiles that already exist from the list."""
    existing_file = tmp_path / "dockerfiles" / "13.2" / "linux" / "Dockerfile"
    existing_file.parent.mkdir(parents=True)
    existing_file.write_text("dummy content")

    to_be_removed_dockerfile = Dockerfile(
        operating_system=OperatingSystem.LINUX,
        nuke_version=13.2,
        nuke_source=None,
    )
    new_dockerfile = Dockerfile(
        operating_system=OperatingSystem.LINUX,
        nuke_version=13.1,
        nuke_source=None,
    )
    test_dockerfiles = [to_be_removed_dockerfile, new_dockerfile]

    _keep_only_new_dockerfiles(tmp_path, test_dockerfiles)

    assert test_dockerfiles == [new_dockerfile]


def test_write_dockerfiles(tmp_path) -> None:
    """Test the writing of dockerfiles to create a Dockerfile."""
    test_dockerfile = Dockerfile(
        operating_system=OperatingSystem.LINUX,
        nuke_version=13.2,
        nuke_source="some data",
    )
    expected_path = tmp_path / "dockerfiles" / "13.2" / "linux" / "Dockerfile"

    assert not expected_path.is_file()
    write_dockerfiles(tmp_path, [test_dockerfile])

    assert expected_path.is_file()
    assert expected_path.read_text() == test_dockerfile.to_dockerfile()


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
            OperatingSystem.MACOS_ARM,
            15.0,
            Path("dockerfiles/15.0/macos_arm/Dockerfile"),
        ),
        (
            OperatingSystem.WINDOWS,
            13.2,
            Path("dockerfiles/13.2/windows/Dockerfile"),
        ),
    ],
)
def test__get_dockerfile_path(
    test_operating_system: OperatingSystem,
    test_nuke_version: float,
    expected_path: Path,
) -> None:
    """Test to return from data object expected path."""
    dockerfile_mock = MagicMock(spec=Dockerfile)
    dockerfile_mock.operating_system = test_operating_system
    dockerfile_mock.nuke_version = test_nuke_version
    assert _get_dockerfile_path(dockerfile_mock) == expected_path
