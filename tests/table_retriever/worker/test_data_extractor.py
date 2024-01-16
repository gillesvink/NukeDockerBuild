"""Tests related to the data extractor.

@maintainer: Gilles Vink
"""
from unittest.mock import patch

import pytest

from table_retriever.datamodel.table_data import DockerImageData
from table_retriever.worker.data_extractor import (
    SizeError,
    TagCollectorError,
    _get_locked_tag,
    _size_calculator,
    manifest_to_docker_image_data,
)


class TestSizeCalculator:
    """Tests related to the size calculator."""

    @staticmethod
    @pytest.mark.parametrize(
        ("test_manifest", "expected_size"),
        [
            (
                {
                    "layers": [
                        {
                            "size": 107_374_182,
                        },
                    ],
                },
                0.1,
            ),
            (
                {
                    "layers": [
                        {
                            "size": 107_374_182,
                        },
                        {
                            "size": 107_374_182,
                        },
                    ],
                },
                0.2,
            ),
            (
                {
                    "layers": [
                        {
                            "size": 100_000_000,
                        },
                        {
                            "size": 200_000_000,
                        },
                        {
                            "size": 200_500_000_00,
                        },
                    ],
                },
                18.952,
            ),
            (
                {
                    "layers": [
                        {
                            "size": 100_020_130,
                        },
                        {
                            "size": 200_000_514,
                        },
                        {
                            "size": 200_500_000_15,
                        },
                    ],
                },
                18.952,
            ),
        ],
    )
    def test_size_calculation(
        test_manifest: dict, expected_size: float
    ) -> None:
        """Test to calculate the size of the provided manifest in gigabytes."""
        assert _size_calculator(test_manifest) == expected_size

    @staticmethod
    def test_size_calculation_without_layers() -> None:
        """Test to raise a SizeError if the layers dont contain size data."""
        with pytest.raises(
            SizeError,
            match="Collected bytes is 0 bytes, which is not possible.",
        ):
            _size_calculator({"layers": {}})


class TestGetLockedTag:
    """Tests related to the get locked tag function."""

    @staticmethod
    @pytest.mark.parametrize(
        ("test_tags", "test_target_tag", "expected_tag"),
        [
            (
                ["13.0-windows-latest", "13.0-windows-1.0"],
                "13.0-windows-latest",
                "13.0-windows-1.0",
            ),
            (
                ["13.0-linux-latest", "13.0-linux-1.0"],
                "13.0-linux-latest",
                "13.0-linux-1.0",
            ),
            (
                ["13.0-linux-slim-latest", "13.0-linux-slim-1.0"],
                "13.0-linux-slim-latest",
                "13.0-linux-slim-1.0",
            ),
            (
                ["13.0-linux-latest", "13.0-linux-1.1"],
                "13.0-linux-latest",
                "13.0-linux-1.1",
            ),
            (
                [
                    "13.0-linux-latest",
                    "13.0-linux-1.1",
                    "13.0-windows-latest",
                    "13.0-windows-1.0",
                ],
                "13.0-linux-latest",
                "13.0-linux-1.1",
            ),
            (
                [
                    "13.0-linux-latest",
                    "13.0-linux-1.1",
                    "13.1-linux-latest",
                    "13.1-linux-1.1",
                ],
                "13.1-linux-latest",
                "13.1-linux-1.1",
            ),
        ],
    )
    def test_expected_return_value(
        test_tags: list[str], test_target_tag: str, expected_tag: str
    ) -> None:
        """Test to get the correct locked tag from the provided 'latest'."""
        assert _get_locked_tag(test_tags, test_target_tag) == expected_tag

    @staticmethod
    def test_no_tag_found() -> None:
        """Test to raise an exception when no tag has been found."""
        with pytest.raises(
            TagCollectorError,
            match="No locked tag found for '13.0-linux-latest'",
        ):
            _get_locked_tag(
                ["13.0-linux-latest", "13.1-linux-1.0"], "13.0-linux-latest"
            )


class TestManifestToDockerImage:
    """Tests related to the manifest to docker image data."""

    @staticmethod
    @pytest.mark.parametrize(
        (
            "test_manifest",
            "test_config",
            "test_tag",
            "test_tags",
            "expected_docker_image_data",
        ),
        [
            (
                {
                    "layers": [
                        {
                            "size": 500_000_000,
                        },
                    ],
                },
                {
                    "config": {
                        "Labels": {
                            "com.nukedockerbuild.nuke_version": "14.0",
                            "com.nukedockerbuild.based_on": "centos:centos7.9.2009",
                            "org.opencontainers.image.created": "2024-01-15",
                            "org.opencontainers.version": "1.0",
                            "com.nukedockerbuild.operating_system": "linux",
                        },
                    }
                },
                "14.0-linux-latest",
                ["14.0-linux-latest", "my_locked_tag"],
                DockerImageData(
                    tag="14.0-linux-latest",
                    locked_tag="my_locked_tag",
                    nuke_version=14.0,
                    target_os="linux",
                    upstream_image="centos:centos7.9.2009",
                    data_added="2024-01-15",
                    image_size=0.5,
                ),
            ),
        ],
    )
    def test_manifest_to_docker_image_data(
        test_manifest: dict,
        test_config: dict,
        test_tag: str,
        test_tags: list[str],
        expected_docker_image_data: DockerImageData,
    ) -> None:
        """Test conversion of manifest to docker image data."""
        with patch(
            "table_retriever.worker.data_extractor._size_calculator",
            return_value=0.5,
        ) as size_calculator_mock, patch(
            "table_retriever.worker.data_extractor._get_locked_tag",
            return_value="my_locked_tag",
        ) as locked_tag_mock:
            assert (
                manifest_to_docker_image_data(
                    manifest=test_manifest,
                    config=test_config,
                    tag=test_tag,
                    all_tags=test_tags,
                )
                == expected_docker_image_data
            )
        size_calculator_mock.assert_called_once_with(test_manifest)
        locked_tag_mock.assert_called_once_with(
            tags=test_tags, target_tag=test_tag
        )
