FROM rockylinux:8

LABEL 'org.opencontainers.version'=1.0
LABEL 'org.opencontainers.image.created'='2024-06-27'
LABEL 'org.opencontainers.image.authors'='gilles@vinkvfx.com'
LABEL 'org.opencontainers.image.description'='Ready to use Docker image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://github.com/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='rockylinux:8'
LABEL 'com.nukedockerbuild.operating_system'='linux'
LABEL 'com.nukedockerbuild.nuke_version'=15.1
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.1v1/Nuke15.1v1-linux-x86_64.tgz'

ARG NUKE_SOURCE_FILES

COPY $NUKE_SOURCE_FILES /usr/local/nuke_install

RUN echo 'Installing required packages.' \
  && dnf install gcc-toolset-11 -y \
  && dnf install cmake3 -y \
  && dnf install mesa-libGLU-devel -y

RUN echo 'Setting devtoolset to gcc-toolset-11.' \
  && echo 'unset BASH_ENV PROMPT_COMMAND ENV && source scl_source enable gcc-toolset-11' >> /usr/bin/scl_enable \
  && echo 'source scl_source enable gcc-toolset-11' >> /etc/bashrc \
  && chmod +x /usr/bin/scl_enable

WORKDIR /nuke_build_directory

ENV CMAKE_PREFIX_PATH=/usr/local/nuke_install \
  BASH_ENV=/usr/bin/scl_enable \
  ENV=/usr/bin/scl_enable \
  PROMPT_COMMAND=/usr/bin/scl_enable
ENV NUKE_VERSION=15.1