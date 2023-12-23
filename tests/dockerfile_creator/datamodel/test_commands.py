"""Script to test the commands file.

@maintainer: Gilles Vink
"""
import pytest

from dockerfile_creator.datamodel.commands import (
    DockerCommand,
    DockerEnvironments,
)


class TestDockerCommand:
    """Tests related to the DockerCommand object."""

    @pytest.mark.parametrize(
        ("test_docker_command", "expected_result"),
        [
            (DockerCommand(["echo hi"]), "RUN echo hi"),
            (DockerCommand(["echo hi", "help"]), "RUN echo hi \\\n  && help"),
            (
                DockerCommand(["echo hi", "help", "command 3"]),
                "RUN echo hi \\\n  && help \\\n  && command 3",
            ),
        ],
    )
    def test_to_docker_format(
        self, test_docker_command: DockerCommand, expected_result: str
    ) -> None:
        """Test to return a string in the docker file format."""
        assert test_docker_command.to_docker_format() == expected_result


class TestDockerEnvironments:
    """Tests related to the DockerEnvironments object."""

    @pytest.mark.parametrize(
        ("test_docker_environments", "expected_result"),
        [
            (DockerEnvironments({"env1": "something"}), "ENV env1=something"),
            (
                DockerEnvironments({"env1": "something", "env2": "hello"}),
                "ENV env1=something \\\n  env2=hello",
            ),
            (
                DockerEnvironments(
                    {"env1": "something", "env2": "hello", "env3": "hi"}
                ),
                "ENV env1=something \\\n  env2=hello \\\n  env3=hi",
            ),
        ],
    )
    def test_to_docker_format(
        self,
        test_docker_environments: DockerEnvironments,
        expected_result: str,
    ) -> None:
        """Test to return a string in the docker file format."""
        assert test_docker_environments.to_docker_format() == expected_result
