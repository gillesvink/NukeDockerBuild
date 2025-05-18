"""File to store commands specifically to its system or image.

@maintainer: Gilles Vink
"""

from __future__ import annotations

from dataclasses import dataclass, field

from nukedockerbuild.datamodel.constants import (
    NUKE_INSTALL_DIRECTORY,
    OperatingSystem,
    UpstreamImage,
)


@dataclass
class DockerCommand:
    """Object to store a docker command."""

    commands: list[str]
    """List of commands related to this RUN command."""
    minimum_version: float | None = None
    """Minimum version it needs to run this command."""
    maximum_version: float | None = None
    """Maximum version that is allowed to run this command."""

    def to_docker_format(self) -> str:
        """Return the object as a string in the docker RUN format."""
        commands_formatted = " \\\n  && ".join(self.commands)
        return f"RUN {commands_formatted}"


@dataclass
class DockerEnvironments:
    """Object to store docker environments"""

    environments: dict[str, str] = field(default_factory=dict)

    def to_docker_format(self) -> str:
        """Return the object as a string in the docker ENV format."""
        formatted_environments = [
            f"{key}={value}" for key, value in self.environments.items()
        ]
        commands_formatted = " \\\n  ".join(formatted_environments)
        return f"ENV {commands_formatted}"


IMAGE_COMMANDS: dict[UpstreamImage, list[DockerCommand]] = {
    UpstreamImage.ROCKYLINUX_8: [  # such an improvement compared to CentOS D:
        DockerCommand(
            [
                "dnf install gcc-toolset-{toolset}-gcc gcc-toolset-{toolset}-gcc-c++ -y",
                "dnf install cmake3 git -y",
                "dnf install mesa-libGLU-devel -y",
                "ln -s /opt/rh/gcc-toolset-{toolset}/root/bin/gcc /usr/bin/gcc",
                "ln -s /opt/rh/gcc-toolset-{toolset}/root/bin/g++ /usr/bin/g++",
                "dnf clean all",
                "rm -rf /var/cache/dnf",
            ]
        ),
    ],
    UpstreamImage.MANYLINUX_2014: [
        DockerCommand(
            [
                "yum install mesa-libGLU-devel -y",
                "yum clean all",
                "rm -rf /var/cache/yum",
            ]
        ),
    ],
}
"""Commands related to each image."""

OS_COMMANDS: dict[OperatingSystem, list[DockerCommand]] = {
    OperatingSystem.LINUX: [],
    OperatingSystem.WINDOWS: [
        DockerCommand(
            [
                "apt-get update",
                "apt-get install wine64 python3 msitools ca-certificates git curl ninja-build winbind -y ",
                "apt-get clean -y",
                "rm -rf /var/lib/apt/lists/*",
                "curl -LO https://github.com/Kitware/CMake/releases/download/v3.29.3/cmake-3.29.3-linux-x86_64.sh",
                "chmod +x cmake-3.29.3-linux-x86_64.sh",
                "./cmake-3.29.3-linux-x86_64.sh --prefix=/usr/local --skip-license",
                "rm cmake-3.29.3-linux-x86_64.sh",
            ]
        ),
        DockerCommand(
            [
                "$(command -v wine64 || command -v wine || false) wineboot --init",
                "while pgrep wineserver > /dev/null; do sleep 1; done",
                # Based on https://github.com/mstorsjo/msvc-wine/blob/master/Dockerfile
            ]
        ),
        DockerCommand(
            [
                "cd ~/",
                "git clone https://github.com/mstorsjo/msvc-wine.git",
                "cd msvc-wine",
                "git checkout 44dc13b5e62ecc2373fbe7e4727a525001f403f4",
                "PYTHONUNBUFFERED=1 ./vsdownload.py --major {toolset} --accept-license --dest /opt/msvc",
                "./install.sh /opt/msvc",
                "mv ./msvcenv-native.sh /opt/msvc",
                "cd ../ && rm -rf ./msvc-wine",
                "bash -c 'export BIN=/opt/msvc/bin/x64/",
                ". /opt/msvc/msvcenv-native.sh",
                'MSVCDIR=$(. "${{BIN}}msvcenv.sh" && echo $MSVCDIR)',
                r"MSVCDIR=${{MSVCDIR//\\\\//}}",
                r"MSVCDIR=${{MSVCDIR#z:}}",
                'echo "export BIN=${{BIN}}" >> /etc/bashrc',
                'echo "export MSVCDIR=$MSVCDIR" >> /etc/bashrc',
                'echo "export CC=${{BIN}}cl" >> /etc/basbashrc',
                'echo "export CXX=${{BIN}}cl" >> /etc/bashrc',
                'echo "export RC=${{BIN}}rc" >> /etc/bashrc',
                'echo "source /opt/msvc/msvcenv-native.sh" >> /etc/bashrc\'',
            ]
        ),
    ],
}
"""Commands related to each operating system."""

OS_ENVIRONMENTS: dict[OperatingSystem, DockerEnvironments] = {
    OperatingSystem.LINUX: DockerEnvironments(
        {
            "CMAKE_PREFIX_PATH": NUKE_INSTALL_DIRECTORY,
            "CXXFLAGS": "-std=c++{cpp_version}",
        }
    ),
    OperatingSystem.WINDOWS: DockerEnvironments(
        {
            "CMAKE_PREFIX_PATH": NUKE_INSTALL_DIRECTORY,
            "PATH": "/opt/msvc/bin/x64:$PATH",
            "GLOBAL_TOOLCHAIN": "/nukedockerbuild/toolchain.cmake",
        }
    ),
}
"""Environment variables related to each operating system."""
