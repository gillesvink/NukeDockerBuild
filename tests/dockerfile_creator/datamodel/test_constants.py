"""Script to test the constants file.

@maintainer: Gilles Vink
"""

import pytest

from dockerfile_creator.datamodel.constants import OperatingSystem


@pytest.mark.parametrize(
    ("test_shortname", "expected_os"),
    [
        ("win", OperatingSystem.WINDOWS),
        ("lin", OperatingSystem.LINUX),
    ],
)
def test_operating_system_from_shortname(
    test_shortname: str, expected_os: OperatingSystem
) -> None:
    """Test to retrieve OperatingSystem from provided short name."""
    assert OperatingSystem.from_shortname(test_shortname) == expected_os


@pytest.mark.parametrize(
    ("test_mapped_name", "expected_os"),
    [
        ("windows_x86", OperatingSystem.WINDOWS),
        ("linux_x86", OperatingSystem.LINUX),
    ],
)
def test_operating_system_from_mapped_name(
    test_mapped_name: str, expected_os: OperatingSystem
) -> None:
    """Test to retrieve OperatingSystem from provided mapped name."""
    assert OperatingSystem.from_mapped_name(test_mapped_name) == expected_os


def test_operating_system_from_shortname_with_invalid_name() -> None:
    """Test to retrieve OperatingSystem from provided short name."""
    with pytest.raises(
        ValueError, match="No matching enum for short name: 'winwows'."
    ):
        assert OperatingSystem.from_shortname("winwows")
