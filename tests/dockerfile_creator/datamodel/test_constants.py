"""Script to test the constants file.

@maintainer: Gilles Vink
"""

import pytest

from dockerfile_creator.datamodel.constants import OperatingSystem


@pytest.mark.parametrize(
    ("test_shortname", "expected_os"),
    [
        ("win", OperatingSystem.WINDOWS),
        ("mac", OperatingSystem.MACOS),
        ("lin", OperatingSystem.LINUX),

    ],
)
def test_operating_system_from_shortname(
    test_shortname: str, expected_os: OperatingSystem
) -> None:
    """Test to retrieve OperatingSystem from provided short name."""
    assert OperatingSystem.from_shortname(test_shortname) == expected_os
