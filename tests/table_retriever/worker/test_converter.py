"""Tests related to the converter.

@maintainer: Gilles Vink
"""


from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from table_retriever.datamodel.table_data import DockerImageData
from table_retriever.worker.converter import (
    _convert_data_to_dataframe,
    _sort_docker_image_data,
    convert_and_sort_data_to_markdown,
)


class TestSorter:
    """Tests related to the sorting of the data objects."""

    @staticmethod
    @pytest.mark.parametrize(
        ("test_version_order", "expected_version_order"),
        [
            ([13.0, 15.0, 14.0], [15.0, 14.0, 13.0]),
            ([13.1, 13.0, 13.2], [13.2, 13.1, 13.0]),
            ([13.1, 15.0, 13.2], [15.0, 13.2, 13.1]),
        ],
    )
    def test_sort_order_by_version(
        test_version_order: list[float], expected_version_order: list[float]
    ) -> None:
        """Test that DockerImage objects are sorted by nuke version."""
        test_data = [
            MagicMock(spec=DockerImageData, nuke_version=version, tag="")
            for version in test_version_order
        ]
        _sort_docker_image_data(test_data)

        assert [
            mock.nuke_version for mock in test_data
        ] == expected_version_order

    @staticmethod
    @pytest.mark.parametrize(
        ("test_version_order", "expected_version_order"),
        [
            (
                ["b", "c", "a"],
                ["a", "b", "c"],
            ),
            (
                ["13.0-windows", "13.0-linux", "13.0-linux-slim"],
                ["13.0-linux", "13.0-linux-slim", "13.0-windows"],
            ),
        ],
    )
    def test_sort_order_by_tag(
        test_version_order: list[float], expected_version_order: list[float]
    ) -> None:
        """Test that DockerImage objects are sorted by tag name."""
        test_data = [
            MagicMock(spec=DockerImageData, tag=tag, nuke_version="")
            for tag in test_version_order
        ]

        _sort_docker_image_data(test_data)

        assert [mock.tag for mock in test_data] == expected_version_order


class TestConvertDockerImageDataToDataframe:
    """Tests related to converting the docker image data to markdown."""

    @staticmethod
    @pytest.mark.parametrize(
        ("test_data", "expected_format"),
        [
            (
                [
                    DockerImageData(
                        "tag",
                        "locked tag",
                        15.0,
                        "target os",
                        "upstream image",
                        "date added",
                        "image size",
                    ),
                ],
                {
                    "Tag": ["tag"],
                    "Locked Tag": ["locked tag"],
                    "Nuke Version": [15.0],
                    "OS": ["target os"],
                    "Upstream Image": ["upstream image"],
                    "Date Added": ["date added"],
                    "Image Size (GB)": ["image size"],
                },
            ),
            (
                [
                    DockerImageData(
                        tag="15.0-linux-latest",
                        locked_tag="15.0-linux-1.0",
                        nuke_version=15.0,
                        target_os="linux",
                        upstream_image="rocky",
                        data_added="date 1",
                        image_size="size 1",
                    ),
                    DockerImageData(
                        tag="15.0-windows-latest",
                        locked_tag="15.0-windows-1.0",
                        nuke_version=15.0,
                        target_os="windows",
                        upstream_image="windows",
                        data_added="date 2",
                        image_size="size 2",
                    ),
                    DockerImageData(
                        tag="14.0-linux-latest",
                        locked_tag="14.0-linux-1.0",
                        nuke_version=14.0,
                        target_os="linux",
                        upstream_image="centos",
                        data_added="date 3",
                        image_size="size 3",
                    ),
                ],
                {
                    "Tag": [
                        "15.0-linux-latest",
                        "15.0-windows-latest",
                        "14.0-linux-latest",
                    ],
                    "Locked Tag": [
                        "15.0-linux-1.0",
                        "15.0-windows-1.0",
                        "14.0-linux-1.0",
                    ],
                    "Nuke Version": [15.0, 15.0, 14.0],
                    "OS": ["linux", "windows", "linux"],
                    "Upstream Image": ["rocky", "windows", "centos"],
                    "Date Added": ["date 1", "date 2", "date 3"],
                    "Image Size (GB)": ["size 1", "size 2", "size 3"],
                },
            ),
        ],
    )
    def test__convert_data_to_dataframe(
        test_data: list[DockerImageData], expected_format: dict
    ) -> None:
        """Test provided list to be translated into DataFrame."""
        expected_dataframe = pd.DataFrame(expected_format)
        assert _convert_data_to_dataframe(test_data).equals(expected_dataframe)


def test_convert_and_sort_data_to_markdown() -> None:
    """Tests sort and convert to be called and return a markdown string."""
    test_data = ["some data"]
    dataframe_mock = MagicMock(spec=pd.DataFrame)
    dataframe_mock.to_markdown.return_value = "hello"
    with patch(
        "table_retriever.worker.converter._sort_docker_image_data"
    ) as sort_mock, patch(
        "table_retriever.worker.converter._convert_data_to_dataframe",
        return_value=dataframe_mock,
    ) as convert_to_dataframe_mock:
        markdown_result = convert_and_sort_data_to_markdown(test_data)

    sort_mock.assert_called_once_with(test_data)
    convert_to_dataframe_mock.assert_called_once_with(test_data)
    dataframe_mock.to_markdown.assert_called_once_with(index=0, floatfmt=(".1f", ".1f", ".1f"))

    assert markdown_result == "\nhello\n"
