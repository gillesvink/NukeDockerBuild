"""Tests related to the retriever script.

@maintainer: Gilles Vink
"""
import contextlib
import json
import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from table_retriever.datamodel.constants import GithubData
from table_retriever.worker.retriever import (
    RetrieveError,
    _get_header,
    _get_requested_data,
    retrieve_manifest,
    retrieve_tags,
)


@pytest.fixture(autouse=True)
def _set_token() -> None:
    """Set test token"""
    os.environ["TOKEN"] = "123"


class TestGetRequestedData:
    """Tests related to the _get_requested_data function."""

    @staticmethod
    def test_call_args() -> None:
        """Tests requests to have been called with the correct args."""
        with patch(
            "table_retriever.worker.retriever.requests"
        ) as requests_mock, patch(
            "table_retriever.worker.retriever._get_header"
        ) as header_mock, contextlib.suppress(
            RetrieveError
        ):
            _get_requested_data(url="hello")

        requests_mock.get.assert_called_once_with(
            url="hello", headers=header_mock(), timeout=3
        )

    @staticmethod
    def test_exception_if_data_not_found() -> None:
        """Test to raise an exception if data could not be found."""
        requests_mock = MagicMock(spec=requests)
        response_mock = MagicMock(spec=requests.Response)
        response_mock.status_code = 403
        requests_mock.get.return_value = response_mock

        with patch(
            "table_retriever.worker.retriever.requests", requests_mock
        ), patch(
            "table_retriever.worker.retriever._get_header"
        ), pytest.raises(
            RetrieveError
        ):
            _get_requested_data(url="hello")


class TestGetHeader:
    """Tests related to the get header function."""

    def test__get_header(self) -> None:
        """Test to return the expected authorization header."""
        requests_mock = MagicMock(spec=requests)
        response_mock = MagicMock(spec=requests.Response)
        response_mock.json.return_value = {"token": "123"}
        requests_mock.get.return_value = response_mock

        with patch("table_retriever.worker.retriever.requests", requests_mock):
            collected_header = _get_header()

        requests_mock.get.assert_called_once_with(
            url=f"https://ghcr.io/token?scope=repository:{GithubData.REPOSITORY.value}:pull",
            timeout=3,
        )
        assert collected_header == {"Authorization": "Bearer 123"}


class TestRetrieveTags:
    """Tests related to the retrieve function."""

    def test__retrieve_tags(self) -> None:
        """Test to call the correct functions."""
        with patch(
            "table_retriever.worker.retriever._get_requested_data",
        ) as response_mock:
            retrieve_tags()
        api_url = f"{GithubData.GHCR_API.value}/tags/list"
        response_mock.assert_called_once_with(url=api_url)

    @pytest.mark.parametrize(
        ("test_data", "expected_data"),
        [
            (
                {
                    "name": "not important",
                    "tags": [
                        "13.0-linux-latest",
                        "13.0-linux-1.0",
                    ],
                },
                {"13.0-linux-latest", "13.0-linux-1.0"},
            ),
            (
                {
                    "name": "not important",
                    "tags": [
                        "13.0-linux-latest",
                        "13.0-linux-1.0",
                        "13.0-linux-1.1",
                    ],
                },
                {"13.0-linux-latest", "13.0-linux-1.1"},
            ),
            (
                {
                    "name": "not important",
                    "tags": [
                        "13.0-windows-latest",
                        "13.0-windows-1.0",
                        "13.0-linux-latest",
                        "13.0-linux-1.0",
                        "13.0-linux-1.1",
                    ],
                },
                {
                    "13.0-windows-latest",
                    "13.0-windows-1.0",
                    "13.0-linux-latest",
                    "13.0-linux-1.1",
                },
            ),
            (
                {
                    "name": "not important",
                    "tags": [
                        "13.0-windows-latest",
                        "13.0-windows-1.0",
                        "14.0-linux-latest",
                        "14.0-linux-1.0",
                        "14.0-linux-1.1",
                    ],
                },
                {
                    "13.0-windows-latest",
                    "13.0-windows-1.0",
                    "14.0-linux-latest",
                    "14.0-linux-1.1",
                },
            ),
            (
                {
                    "name": "it really is not important",
                    "tags": [
                        "13.0-windows-latest",
                        "13.0-windows-1.0",
                        "14.0-linux-latest",
                        "14.0-linux-1.0",
                        "14.0-linux-1.1",
                        "14.0-linux-slim-latest",
                        "14.0-linux-slim-1.0",
                        "14.0-linux-slim-1.1",
                    ],
                },
                {
                    "13.0-windows-latest",
                    "13.0-windows-1.0",
                    "14.0-linux-latest",
                    "14.0-linux-1.1",
                    "14.0-linux-slim-latest",
                    "14.0-linux-slim-1.1",
                },
            ),
        ],
    )
    def test__return_value(self, test_data: dict, expected_data: dict) -> None:
        """Test to return the expected data and strip redundant data."""
        response_mock = MagicMock(spec=requests.Response)
        response_mock.json.return_value = test_data

        with patch(
            "table_retriever.worker.retriever._get_requested_data",
            return_value=response_mock,
        ):
            retrieved_data = retrieve_tags()

        assert isinstance(retrieved_data, set)
        assert retrieved_data == expected_data


class TestRetrieveDockerImageData:
    """Tests related to the retrieve docker image data function."""

    def test__retrieve_manifest(self) -> None:
        """Test to retrieve the manifest for a specific tag."""
        with patch(
            "table_retriever.worker.retriever._get_requested_data"
        ) as get_requested_data_mock:
            retrieve_manifest(tag="15.0-linux-latest")

        expected_url = (
            f"{GithubData.GHCR_API.value}/manifests/15.0-linux-latest"
        )
        get_requested_data_mock.assert_called_once_with(url=expected_url)

    @pytest.mark.parametrize(
        "test_data",
        [
            {
                "layers": [
                    {
                        "size": 1388598786,
                    },
                ],
                "labels": {
                    "hey": "hello",
                    "how are you": "good",
                },
            }
        ],
    )
    def test_return_data(self, test_data: str) -> None:
        """Test retrieve manifest to convert json to dict and strip data."""
        response_mock = MagicMock(spec=requests.Response)
        response_mock.json.return_value = test_data

        with patch(
            "table_retriever.worker.retriever._get_requested_data",
            return_value=response_mock,
        ):
            retrieved_data = retrieve_manifest("some_tag")

        assert retrieved_data == test_data
