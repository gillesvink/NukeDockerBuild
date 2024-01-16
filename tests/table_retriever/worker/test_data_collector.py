"""Tests related to the data collector.

@maintainer: Gilles Vink
"""


from unittest.mock import MagicMock, patch

from table_retriever.worker.data_collector import get_all_docker_image_data


class TestGetAllDockerImageData:
    """Test the function that is responsible for calling all functions."""

    @staticmethod
    def test_call_args() -> None:
        """Tests that all the associated functions have been called."""
        test_tags = ["13.0-linux-latest", "13.0-linux-1.0"]
        manifests_mock = MagicMock()
        manifests_mock.return_value = {"manifests": "return_data"}
        config_mock = MagicMock()
        config_mock.return_value = {"config": "return_data"}
        manifests_to_docker_image_data_mock = MagicMock()

        with patch(
            "table_retriever.worker.data_collector.retrieve_tags",
            return_value=test_tags,
        ), patch(
            "table_retriever.worker.data_collector.retrieve_manifest",
            manifests_mock,
        ), patch(
            "table_retriever.worker.data_collector.retrieve_config_from_manifest",
            config_mock,
        ), patch(
            "table_retriever.worker.data_collector.manifest_to_docker_image_data",
            manifests_to_docker_image_data_mock,
        ):
            get_all_docker_image_data()

        manifests_mock.assert_called_once_with("13.0-linux-latest")
        config_mock.assert_called_once_with({"manifests": "return_data"})
        manifests_to_docker_image_data_mock.assert_called_once_with(
            manifest={"manifests": "return_data"},
            config={"config": "return_data"},
            tag="13.0-linux-latest",
            all_tags=test_tags,
        )

    @staticmethod
    def test_to_skip_if_latest_not_in_tag() -> None:
        """Test to skip processing in latest is not in tag list."""
        with patch(
            "table_retriever.worker.data_collector.retrieve_tags",
            return_value=["13.0-linux-1.0", "15.0-linux-1.1"],
        ), patch(
            "table_retriever.worker.data_collector.retrieve_manifest"
        ) as first_function_to_be_called:
            get_all_docker_image_data()

        assert first_function_to_be_called.call_count == 0
