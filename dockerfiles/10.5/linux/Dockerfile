FROM quay.io/pypa/manylinux2014_x86_64

LABEL 'org.opencontainers.version'=1.1
LABEL 'org.opencontainers.image.created'='2025-05-18'
LABEL 'org.opencontainers.image.description'='Ready to use image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://codeberg.org/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='quay.io/pypa/manylinux2014_x86_64'
LABEL 'com.nukedockerbuild.operating_system'='linux'
LABEL 'com.nukedockerbuild.nuke_version'=10.5
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/10.5v8/Nuke10.5v8-linux-x86-release-64.tgz'

ARG NUKE_SOURCE_FILES

COPY $NUKE_SOURCE_FILES /usr/local/nuke_install

RUN yum install mesa-libGLU-devel -y \
  && yum clean all \
  && rm -rf /var/cache/yum

WORKDIR /nuke_build_directory

ENV CMAKE_PREFIX_PATH=/usr/local/nuke_install \
  CXXFLAGS=-std=c++11
ENV NUKE_VERSION=10.5