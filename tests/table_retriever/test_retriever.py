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
from table_retriever.worker.retriever import RetrieveError, _retrieve_tags


@pytest.fixture(autouse=True)
def _set_token() -> None:
    """Set test token"""
    os.environ["TOKEN"] = "123"


class TestRetrieveTags:
    """Tests related to the retrieve function."""

    def test__retrieve_tags(self) -> None:
        """Test to call the correct functions."""
        os_mock = MagicMock(spec=os)
        os_mock.environ.__getitem__.return_value = "123"
        with patch(
            "table_retriever.worker.retriever.requests"
        ) as requests_mock, patch(
            "table_retriever.worker.retriever.os", os_mock
        ), contextlib.suppress(
            RetrieveError
        ):
            _retrieve_tags()
        expected_headers = {"Authorization": "Bearer 123"}
        api_url = f"{GithubData.GHCR_API.value}/tags/list"
        requests_mock.get.assert_called_once_with(
            api_url, headers=expected_headers, timeout=3
        )
        os_mock.environ.__getitem__.assert_called_once_with("TOKEN")

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
                    "name": "not important",
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
