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
                "dnf install {toolset} -y",
                "dnf install cmake3 git -y",
                "dnf install mesa-libGLU-devel -y",
                "dnf clean all",
                "rm -rf /var/cache/dnf",
            ]
        ),
    ],
    UpstreamImage.CENTOS_7_9: [
        DockerCommand(
            [
                "ulimit -n 1024",
                "sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/*.repo",
                "sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/*.repo",
                "sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/*.repo",
                "yum -y install centos-release-scl-rh ",
                (
                    r"sed -i 's/7/7.4.1708/g; s|^#\s*\(baseurl=http://\)mirror"
                    r"|\1vault|g; /mirrorlist/d' "
                    "/etc/yum.repos.d/CentOS-SCLo-*.repo"
                ),
                "yum -y install {toolset}",
                "yum clean all",
                "rm -rf /var/cache/yum",
            ]
        ),
        DockerCommand(
            [
                "ulimit -n 1024",
                "yum update -y",
                "yum -y install epel-release",
                "yum -y install mesa-libGLU-devel make",
                "cd /tmp/",
                "curl -LO https://github.com/Kitware/CMake/releases/download/v3.27.7/cmake-3.27.7-linux-x86_64.sh",
                "chmod +x cmake-3.27.7-linux-x86_64.sh",
                "./cmake-3.27.7-linux-x86_64.sh --prefix=/usr/local --skip-license",
                "rm cmake-3.27.7-linux-x86_64.sh",
                "yum clean all",
                "rm -rf /var/cache/yum",
            ]
        ),
        DockerCommand(
            [
                "ulimit -n 1024",
                "yum update -y",
                "yum install -y autoconf curl-devel expat-devel gettext-devel openssl-devel zlib-devel perl-CPAN perl-devel xz",
                "cd /tmp",
                "curl -LO https://www.kernel.org/pub/software/scm/git/git-2.9.5.tar.xz",
                "tar xf git-2.9.5.tar.xz",
                "rm git-2.9.5.tar.xz",
                "cd git-2.9.5",
                "make configure",
                "source scl_source enable {toolset}",
                "./configure --prefix=/usr/local",
                "make all",
                "make install",
                "cd ../",
                "rm -rf git-2.9.5",
                "yum clean all",
                "rm -rf /var/cache/yum",
            ]
        ),
    ],
    UpstreamImage.CENTOS_7_4: [
        DockerCommand(
            [
                "ulimit -n 1024",
                "sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/*.repo",
                "sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/*.repo",
                "sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/*.repo",
                "yum -y install centos-release-scl-rh ",
                "echo 'Use vault for SC packages as CentOS 7 reached EOL.'",
                (
                    r"sed -i 's/7/7.4.1708/g; s|^#\s*\(baseurl=http://\)mirror"
                    r"|\1vault|g; /mirrorlist/d' "
                    "/etc/yum.repos.d/CentOS-SCLo-*.repo"
                ),
                "yum -y install {toolset}",
                "yum clean all",
                "rm -rf /var/cache/yum",
            ]
        ),
        DockerCommand(
            [
                "ulimit -n 1024",
                "yum update -y",
                "yum -y install epel-release",
                "yum -y install mesa-libGLU-devel make",
                "cd /tmp/",
                "curl -LO https://github.com/Kitware/CMake/releases/download/v3.27.7/cmake-3.27.7-linux-x86_64.sh",
                "chmod +x cmake-3.27.7-linux-x86_64.sh",
                "./cmake-3.27.7-linux-x86_64.sh --prefix=/usr/local --skip-license",
                "rm cmake-3.27.7-linux-x86_64.sh",
                "yum clean all",
                "rm -rf /var/cache/yum",
            ]
        ),
        DockerCommand(
            [
                "ulimit -n 1024",
                "yum update -y",
                "yum install -y autoconf curl-devel expat-devel gettext-devel openssl-devel zlib-devel perl-CPAN perl-devel xz",
                "cd /tmp",
                "curl -LO https://www.kernel.org/pub/software/scm/git/git-2.9.5.tar.xz",
                "tar xf git-2.9.5.tar.xz",
                "rm git-2.9.5.tar.xz",
                "cd git-2.9.5",
                "source scl_source enable {toolset}",
                "make configure",
                "./configure --prefix=/usr/local",
                "make all",
                "make install",
                "cd ../",
                "rm -rf git-2.9.5",
                "yum clean all",
                "rm -rf /var/cache/yum",
            ],
            minimum_version=12.0,
        ),
        DockerCommand(
            [
                "ulimit -n 1024",
                "yum update -y",
                "yum install -y autoconf curl-devel expat-devel gettext-devel openssl-devel zlib-devel perl-CPAN perl-devel xz",
                "cd /tmp",
                "curl -LO https://www.kernel.org/pub/software/scm/git/git-2.9.5.tar.xz",
                "tar xf git-2.9.5.tar.xz",
                "rm git-2.9.5.tar.xz",
                "cd git-2.9.5",
                "make configure",
                "./configure --prefix=/usr/local",
                "make all",
                "make install",
                "cd ../",
                "rm -rf git-2.9.5",
                "yum clean all",
                "rm -rf /var/cache/yum",
            ],
            maximum_version=11.3,
        ),
    ],
}
"""Commands related to each image."""

OS_COMMANDS: dict[OperatingSystem, list[DockerCommand]] = {
    OperatingSystem.LINUX: [
        DockerCommand(
            commands=[
                "echo 'source scl_source enable {toolset}' >> /usr/bin/scl_enable",
                "echo 'source /usr/bin/scl_enable' >> /etc/bashrc",
                "chmod +x /usr/bin/scl_enable",
            ],
            minimum_version=12,
        ),
    ],
    OperatingSystem.WINDOWS: [
        DockerCommand(
            [
                "apt-get update",
                "apt-get install wine64 python3 msitools ca-certificates git wget ninja-build winbind -y ",
                "apt-get clean -y",
                "rm -rf /var/lib/apt/lists/*",
                "wget https://github.com/Kitware/CMake/releases/download/v3.29.3/cmake-3.29.3-linux-x86_64.sh",
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
            "BASH_ENV": "/usr/bin/scl_enable",
            "ENV": "/usr/bin/scl_enable",
            "PROMPT_COMMAND": "/usr/bin/scl_enable",
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
