"""File to store commands specifically to its system or image.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dockerfile_creator.datamodel.constants import (
    NUKE_INSTALL_DIRECTORIES,
    OperatingSystem,
    UpstreamImage,
)


@dataclass
class DockerCommand:
    """Object to store a docker command."""

    commands: list[str] = field(default_factory=list)
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
                "echo 'Installing required packages.'",
                "dnf install {toolset} -y",
                "dnf install cmake3 -y",
                "dnf install mesa-libGLU-devel -y",
            ]
        ),
    ],
    UpstreamImage.CENTOS_7_9: [
        DockerCommand(
            [
                "echo 'Installing required packages.'",
                "ulimit -n 1024",
                "yum -y install epel-release",
                "yum -y install centos-release-scl",
                "yum -y install {toolset}",
                "yum -y install cmake3",
                "yum -y install mesa-libGLU-devel",
            ]
        ),
    ],
    UpstreamImage.CENTOS_7_4: [
        DockerCommand(
            [
                "echo 'Installing required packages.'",
                "ulimit -n 1024",
                "yum -y install epel-release",
                "yum -y install cmake3",
                "yum -y install mesa-libGLU-devel",
            ]
        ),
        DockerCommand(
            [
                "echo 'Installing devtoolset.'",
                "ulimit -n 1024",
                "yum -y install centos-release-scl-rh ",
                "echo 'Use vault for SC packages as CentOS 7 reached EOL.'",
                (
                    r"sed -i 's/7/7.4.1708/g; s|^#\s*\(baseurl=http://\)mirror"
                    r"|\1vault|g; /mirrorlist/d' "
                    "/etc/yum.repos.d/CentOS-SCLo-*.repo"
                ),
                "yum -y install {toolset}",
            ]
        ),
    ],
}
"""Commands related to each image."""

OS_COMMANDS: dict[OperatingSystem, list[DockerCommand]] = {
    OperatingSystem.LINUX: [
        DockerCommand(
            [
                "echo 'Setting devtoolset to {toolset}.'",
                "echo 'unset BASH_ENV PROMPT_COMMAND ENV && source scl_source "
                "enable {toolset}' >> /usr/bin/scl_enable",
                "echo 'source scl_source enable {toolset}' >> /etc/bashrc",
                "chmod +x /usr/bin/scl_enable",
            ]
        ),
    ],
    OperatingSystem.WINDOWS: [
        DockerCommand(
            [
                r'powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('
                "'https://community.chocolatey.org/install.ps1'))"
                r'" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"',
                "choco install cmake --installargs 'ADD_CMAKE_TO_PATH=System' -y",
                "choco install visualstudio{toolset}buildtools -y",
                "choco install visualstudio{toolset}-workload-vctools --package-parameters '--includeRecommended' -y",
                'powershell -Command "Remove-Item -Path \\"$env:TEMP\\*\\" -Force -Recurse"',
                "powershell -Command \"Remove-Item -Path 'C:\\ProgramData\\Package Cache\\*' -Force -Recurse\"",
            ],
            minimum_version=13.0,
        ),
    ],
    OperatingSystem.MACOS: [
        DockerCommand(
            [
                "apt-get update",
                "apt-get install -y cmake git python3 patch libssl-dev lzma-dev libxml2-dev bzip2 cpio zlib1g-dev curl clang unzip build-essential",
                "cd /tmp/ && git clone https://github.com/tpoechtrager/osxcross",
                "cd /tmp/osxcross/tarballs && curl -LO {toolset}",
                "cd /tmp/osxcross && UNATTENDED=1 TARGET_DIR=/usr/local/osxcross ./build.sh",
                "apt-get -y remove python3 git patch libssl-dev lzma-dev libxml2-dev bzip2 cpio zlib1g-dev curl unzip build-essential",
                "apt-get -y autoremove",
                "apt-get -y clean",
                "rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*",
            ]
        ),
    ],
}
"""Commands related to each operating system."""

OS_ENVIRONMENTS: dict[OperatingSystem, DockerEnvironments] = {
    OperatingSystem.LINUX: DockerEnvironments(
        {
            "CMAKE_PREFIX_PATH": NUKE_INSTALL_DIRECTORIES[
                OperatingSystem.LINUX
            ],
            "BASH_ENV": "/usr/bin/scl_enable",
            "ENV": "/usr/bin/scl_enable",
            "PROMPT_COMMAND": "/usr/bin/scl_enable",
        }
    ),
    OperatingSystem.WINDOWS: DockerEnvironments(
        {
            "CMAKE_PREFIX_PATH": NUKE_INSTALL_DIRECTORIES[
                OperatingSystem.WINDOWS
            ],
        }
    ),
    OperatingSystem.MACOS: DockerEnvironments(
        {
            "CMAKE_PREFIX_PATH": NUKE_INSTALL_DIRECTORIES[
                OperatingSystem.LINUX
            ],
            "PATH": "/usr/local/osxcross/bin:$PATH",
            "GLOBAL_TOOLCHAIN": "/nukedockerbuild/toolchain.cmake",
        }
    ),
}
"""Environment variables related to each operating system."""
