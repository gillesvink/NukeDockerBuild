FROM rockylinux:8

LABEL 'org.opencontainers.version'=1.2
LABEL 'org.opencontainers.image.created'='2025-05-18'
LABEL 'org.opencontainers.image.description'='Ready to use image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://codeberg.org/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='rockylinux:8'
LABEL 'com.nukedockerbuild.operating_system'='linux'
LABEL 'com.nukedockerbuild.nuke_version'=15.1
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.1v7/Nuke15.1v7-linux-x86_64.tgz'

ARG NUKE_SOURCE_FILES

COPY $NUKE_SOURCE_FILES /usr/local/nuke_install

RUN dnf install gcc-toolset-11-gcc gcc-toolset-11-gcc-c++ -y \
  && dnf install cmake3 git -y \
  && dnf install mesa-libGLU-devel -y \
  && ln -s /opt/rh/gcc-toolset-11/root/bin/gcc /usr/bin/gcc \
  && ln -s /opt/rh/gcc-toolset-11/root/bin/g++ /usr/bin/g++ \
  && dnf clean all \
  && rm -rf /var/cache/dnf

WORKDIR /nuke_build_directory

ENV CMAKE_PREFIX_PATH=/usr/local/nuke_install \
  CXXFLAGS=-std=c++17
ENV NUKE_VERSION=15.1