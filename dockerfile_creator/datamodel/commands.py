"""File to store commands specifically to its system or image.

@maintainer: Gilles Vink
"""

from dataclasses import dataclass, field

from dockerfile_creator.datamodel.constants import (
    NUKE_INSTALL_DIRECTORIES,
    REDUNDANT_NUKE_ITEMS,
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
                "echo 'Downloading Nuke from {url}'.",
                "curl -o /tmp/{filename}.tgz {url}",
                "echo 'Extracting and installing Nuke ({filename})'.",
                "tar zxvf /tmp/{filename}.tgz -C /tmp",
                f"mkdir {NUKE_INSTALL_DIRECTORIES[OperatingSystem.LINUX]}",
                (
                    "/tmp/{filename}.run "
                    "--accept-foundry-eula --prefix="
                    f"{NUKE_INSTALL_DIRECTORIES[OperatingSystem.LINUX]} "
                    "--exclude-subdir"
                ),
                "echo 'Cleaning up Nuke to reduce image size.'",
                "rm -rf /tmp/*",
                f"cd {NUKE_INSTALL_DIRECTORIES[OperatingSystem.LINUX]}",
                (
                    f"cp -r {NUKE_INSTALL_DIRECTORIES[OperatingSystem.LINUX]}"
                    "/Documentation/NDKExamples/examples/ /nuke_tests/"
                ),
                f"rm -rf {REDUNDANT_NUKE_ITEMS}",
            ]
        ),
        DockerCommand(
            [
                "echo 'Setting devtoolset to {toolset}.'",
                "echo 'unset BASH_ENV PROMPT_COMMAND ENV && source scl_source "
                "enable {toolset}' >> /usr/bin/scl_enable",
            ]
        ),
    ],
    OperatingSystem.WINDOWS: [
        DockerCommand(
            [
                "mkdir C:\\temp",
                "curl -o C:\\temp{filename}.zip {url}",
                "cd C:\\temp",
                "tar -xf {filename}.zip",
                "msiexec.exe /i {filename}.msi ACCEPT_FOUNDRY_EULA=ACCEPT "
                f"INSTALL_ROOT={NUKE_INSTALL_DIRECTORIES[OperatingSystem.WINDOWS]} /qb /l log.txt",
                "ping -n 10 127.0.0.1",  # let the process finish so wait.
                f"cd {NUKE_INSTALL_DIRECTORIES[OperatingSystem.WINDOWS]}",
                "del /q",
                "rmdir C:\\temp /s /q",
            ],
            minimum_version=14.0,
        ),
        DockerCommand(
            [
                "mkdir C:\\temp",
                "curl -o C:\\temp\\{filename}.zip {url}",
                "cd C:\\temp",
                "tar -xf {filename}.zip",
                "msiexec.exe /i {filename}.msi ACCEPT_FOUNDRY_EULA=ACCEPT "
                f"/dir {NUKE_INSTALL_DIRECTORIES[OperatingSystem.WINDOWS]} /silent /l log.txt",
                "ping -n 10 127.0.0.1",
                f"cd {NUKE_INSTALL_DIRECTORIES[OperatingSystem.WINDOWS]}",
                "del /q",
                "rmdir C:\\temp /s /q",
            ],
            maximum_version=13.9,
        ),
        DockerCommand(
            [
                r'"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"',
                "choco install cmake --installargs 'ADD_CMAKE_TO_PATH=System' -y",
                "choco install visualstudio{toolset}buildtools -y",
                "choco install visualstudio{toolset}-workload-vctools --package-parameters '--includeRecommended' -y",
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
}
"""Environment variables related to each operating system."""
