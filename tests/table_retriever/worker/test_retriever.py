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
    _retrieve_tags,
    _get_header,
    _retrieve_manifest,
)


@pytest.fixture(autouse=True)
def _set_token() -> None:
    """Set test token"""
    os.environ["TOKEN"] = "123"


class TestGetHeader:
    """Tests related to the get header function."""

    def test__get_header(self) -> None:
        """Test to return the expected authorization header."""
        os_mock = MagicMock(spec=os)
        os_mock.getenv.return_value = "123"
        with patch("table_retriever.worker.retriever.os", os_mock):
            collected_header = _get_header()
        os_mock.getenv.assert_called_once_with("TOKEN")
        assert collected_header == {"Authorization": "Bearer 123"}

    def test__no_token_environment_set(self) -> None:
        """Test to raise an exception when no token env has been set."""
        os.environ["TOKEN"] = ""
        with pytest.raises(
            RetrieveError, match="No TOKEN environment has been set."
        ):
            _get_header()


class TestRetrieveTags:
    """Tests related to the retrieve function."""

    def test__retrieve_tags(self) -> None:
        """Test to call the correct functions."""
        with patch(
            "table_retriever.worker.retriever.requests"
        ) as requests_mock, patch(
            "table_retriever.worker.retriever._get_header",
        ) as get_header_mock, contextlib.suppress(
            RetrieveError
        ):
            _retrieve_tags()
        api_url = f"{GithubData.GHCR_API.value}/tags/list"
        requests_mock.get.assert_called_once_with(
            url=api_url, headers=get_header_mock(), timeout=3
        )

    def test__retrieve_tags_no_data_found(self) -> None:
        """Test to raise a RetrieveError if status code is not 200"""
        requests_mock = MagicMock(spec=requests)
        response_mock = MagicMock(spec=requests.Response)
        response_mock.status_code = 404
        requests_mock.get.return_value = response_mock
        with patch(
            "table_retriever.worker.retriever.requests", requests_mock
        ), pytest.raises(RetrieveError, match="No data found on server."):
            _retrieve_tags()

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
        requests_mock = MagicMock(requests)
        response_mock = MagicMock(spec=requests.Response)
        response_mock.status_code = 200
        response_mock.json.return_value = json.dumps(test_data)
        requests_mock.get.return_value = response_mock

        with patch("table_retriever.worker.retriever.requests", requests_mock):
            retrieved_data = _retrieve_tags()

        assert isinstance(retrieved_data, set)
        assert retrieved_data == expected_data


class TestRetrieveDockerImageData:
    """Tests related to the retrieve docker image data function."""

    def test__retrieve_manifest(self) -> None:
        """Test to retrieve the manifest for a specific tag."""
        with patch(
            "table_retriever.worker.retriever.requests"
        ) as requests_mock, contextlib.suppress(RetrieveError):
            _retrieve_manifest(tag="15.0-linux-latest")

        expected_url = f"{GithubData.GHCR_API}/manifests/15.0-linux-latest"
        requests_mock.get.assert_called_once_with(
            url=expected_url, headers=_get_header(), timeout=3
        )

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
        requests_mock = MagicMock(requests)
        response_mock = MagicMock(spec=requests.Response)
        response_mock.status_code = 200
        response_mock.json.return_value = json.dumps(test_data)
        requests_mock.get.return_value = response_mock

        with patch("table_retriever.worker.retriever.requests", requests_mock):
            retrieved_data = _retrieve_manifest("some_tag")

        assert retrieved_data == test_data

    def test_to_raise_exception_if_data_not_found(self) -> None:
        """Test to raise a RetrieveError if the data is not found."""
        requests_mock = MagicMock(spec=requests)
        response_mock = MagicMock(spec=requests.Response)
        response_mock.status_code = 404
        requests_mock.get.return_value = response_mock
        with patch(
            "table_retriever.worker.retriever.requests", requests_mock
        ), pytest.raises(
            RetrieveError, match="No data found for tag 'some_tag'."
        ):
            _retrieve_manifest("some_tag")

