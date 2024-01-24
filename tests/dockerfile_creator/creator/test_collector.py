"""Tests related to the collector script.

@maintainer: Gilles Vink
"""

from unittest.mock import MagicMock, patch

import pytest
from requests import Response

from dockerfile_creator.creator.collector import (
    _nuke_version_to_float,
    fetch_json_data,
    get_dockerfiles,
)
from dockerfile_creator.datamodel.constants import (
    JSON_DATA_SOURCE,
    OperatingSystem,
)
from dockerfile_creator.datamodel.docker_data import Dockerfile


@pytest.fixture(autouse=True)
def _mock_requests():
    """Automatically patch every test to prevent actual calls."""
    with patch("dockerfile_creator.creator.collector.requests.get"):
        yield


@pytest.fixture()
def dummy_data() -> dict:
    """Example data that would be fetched in the json requests."""
    return {
        "15": {
            "15.1v5": {
                "installer": {
                    "mac_x86": "mac_url",
                    "mac_arm": "mac_arm_url",
                }
            },
            "15.0v2": {
                "installer": {
                    "mac_x86": "mac_url",
                    "linux_x86": "linux_url",
                    "windows_x86": "windows_url",
                },
            },
        },
        "14": {
            "14.1v2": {
                "installer": {
                    "mac_x86": "mac_url",
                    "mac_arm": None,
                    "linux_x86": "linux_url",
                    "windows_x86": "windows_url",
                },
            },
        },
    }


def test_fetch_json_data(dummy_data: dict) -> None:
    """Test to make requests to Github and collect JSON."""
    response_mock = MagicMock(spec=Response)
    response_mock.json.return_value = dummy_data
    response_mock.status_code = 200
    with patch(
        "dockerfile_creator.creator.collector.requests.get",
        return_value=response_mock,
    ) as requests_get_mock:
        collected_data = fetch_json_data()
    requests_get_mock.assert_called_once_with(JSON_DATA_SOURCE, timeout=10)
    assert collected_data == dummy_data


@pytest.mark.parametrize("test_status_code", [403, 404])
def test_fetch_json_data_but_no_data_found(test_status_code: int) -> None:
    """Test to make sure we raise an exception when data is not found."""
    requests_get_mock = MagicMock(spec=Response)
    requests_get_mock.status_code = test_status_code
    with patch(
        "dockerfile_creator.creator.collector.requests.get",
        return_value=requests_get_mock,
    ), pytest.raises(
        ValueError,
        match="Request returned 404. Please check the URL and try again.",
    ):
        fetch_json_data()


@pytest.mark.parametrize(
    ("test_nuke_version", "expected_float"),
    [
        ("10.0v2", 10.0),
        ("15.5v51", 15.5),
        ("9.1v3", 9.1),
    ],
)
def test__nuke_version_to_float(
    test_nuke_version: str, expected_float: float
) -> None:
    """Test to convert string Nuke version to float."""
    assert _nuke_version_to_float(test_nuke_version) == expected_float


def test__nuke_version_to_float_raise_exception() -> None:
    """Test to raise an exception if no 'v' could be found."""
    with pytest.raises(
        ValueError, match="Provided data is not a valid version. '10.0b1'"
    ):
        _nuke_version_to_float("10.0b1")


def test_get_dockerfiles(dummy_data: dict) -> None:
    """Test to return from the dummy data a list of Dockerfile."""
    expected_dockerfiles = [
        Dockerfile(
            operating_system=OperatingSystem.MACOS_ARM,
            nuke_version=15.1,
            nuke_source="mac_arm_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.MACOS,
            nuke_version=15.1,
            nuke_source="mac_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.MACOS,
            nuke_version=15.0,
            nuke_source="mac_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.LINUX,
            nuke_version=15.0,
            nuke_source="linux_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.WINDOWS,
            nuke_version=15.0,
            nuke_source="windows_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.MACOS,
            nuke_version=14.1,
            nuke_source="mac_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.LINUX,
            nuke_version=14.1,
            nuke_source="linux_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.WINDOWS,
            nuke_version=14.1,
            nuke_source="windows_url",
        ),
    ]
    assert get_dockerfiles(dummy_data) == expected_dockerfiles


def test_get_dockerfiles_but_skip_12() -> None:
    """Test to not include version 12 as this is not valid for images."""
    dummy_data = {
        "15": {
            "15.0v2": {
                "installer": {
                    "linux_x86": "linux_url",
                },
            },
        },
        "12": {
            "12.0v2": {
                "installer": {
                    "linux_x86": "linux_url",
                },
            },
        },
    }
    expected_dockerfiles = [
        Dockerfile(
            operating_system=OperatingSystem.LINUX,
            nuke_version=15.0,
            nuke_source="linux_url",
        ),
    ]
    assert get_dockerfiles(dummy_data) == expected_dockerfiles
