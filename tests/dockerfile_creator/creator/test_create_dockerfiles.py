"""Tests for the script that creates the dockerfiles."""
from pathlib import Path

from dockerfile_creator.creator.create_dockerfiles import (
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
