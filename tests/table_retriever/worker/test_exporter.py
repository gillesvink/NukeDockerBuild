"""Tests related to the table retriever exporter.

@maintainer: Gilles Vink
"""
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from table_retriever.worker.exporter import (
    _replace_between_comments,
    replace_text_in_markdown,
)


class TestReplaceBetweenComments:
    """Tests related to the replace between comments function."""

    @staticmethod
    def test_replace_everything_between_comments() -> None:
        """Test to replace everything with the provided string."""
        test_string = """
    This is some text I'd like to keep

    <!-- TABLE_START -->
    this text should be replaced
    <!-- TABLE_END -->

    however, surprise surprise, this text should stay
    """
        replacement_string = """
    this should be added
    even with multi lines like a table
    """
        result = _replace_between_comments(test_string, replacement_string)

        assert (
            result
            == """
    This is some text I'd like to keep

    <!-- TABLE_START -->
    this should be added
    even with multi lines like a table
    <!-- TABLE_END -->

    however, surprise surprise, this text should stay
    """
        )

    @staticmethod
    def test_raise_exception_for_invalid_input_text() -> None:
        """Test to raise RuntimeError if replacement position is invalid."""
        with pytest.raises(
            RuntimeError,
            match="Provided string is not able to find replacement position.",
        ):
            _replace_between_comments("", "hello")


class TestWriteReplacement:
    """Tests related to the replace_text_in_markdown function."""

    @staticmethod
    def test_function_calls() -> None:
        """Test that replacement functions have been called and written."""

        pathlib_mock = MagicMock(spec=Path)
        with patch(
            "table_retriever.worker.exporter._replace_between_comments"
        ) as replace_mock:
            replace_text_in_markdown(
                path=pathlib_mock, replace_content="my_new_text"
            )

        pathlib_mock.read_text.assert_called_once_with(encoding="utf-8")
        replace_mock.assert_called_once_with(
            pathlib_mock.read_text(), "my_new_text"
        )
        pathlib_mock.write_text.assert_called_once_with(
            replace_mock(), encoding="utf-8"
        )
