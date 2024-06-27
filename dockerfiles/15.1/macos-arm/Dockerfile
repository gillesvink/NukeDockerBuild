FROM debian:bookworm

LABEL 'org.opencontainers.version'=1.0
LABEL 'org.opencontainers.image.created'='2024-06-27'
LABEL 'org.opencontainers.image.authors'='gilles@vinkvfx.com'
LABEL 'org.opencontainers.image.description'='Ready to use Docker image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://github.com/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='debian:bookworm'
LABEL 'com.nukedockerbuild.operating_system'='macos-arm'
LABEL 'com.nukedockerbuild.nuke_version'=15.1
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.1v1/Nuke15.1v1-mac-arm64.dmg'

ARG NUKE_SOURCE_FILES
ARG TOOLCHAIN

COPY $NUKE_SOURCE_FILES /usr/local/nuke_install
COPY $TOOLCHAIN /nukedockerbuild/

RUN apt-get update \
  && apt-get install -y cmake git python3 patch libssl-dev lzma-dev libxml2-dev bzip2 cpio zlib1g-dev curl clang unzip build-essential \
  && cd /tmp/ && git clone https://github.com/tpoechtrager/osxcross \
  && cd /tmp/osxcross/tarballs && curl -LO https://github.com/joseluisq/macosx-sdks/releases/download/13.3/MacOSX13.3.sdk.tar.xz \
  && cd /tmp/osxcross && UNATTENDED=1 TARGET_DIR=/usr/local/osxcross ./build.sh \
  && apt-get -y remove python3 git patch libssl-dev lzma-dev libxml2-dev bzip2 cpio zlib1g-dev curl unzip build-essential \
  && apt-get -y autoremove \
  && apt-get -y clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /nuke_build_directory

ENV CMAKE_PREFIX_PATH=/usr/local/nuke_install \
  PATH=/usr/local/osxcross/bin:$PATH \
  GLOBAL_TOOLCHAIN=/nukedockerbuild/toolchain.cmake
ENV NUKE_VERSION=15.1 \
  MACOS_SDK=/usr/local/osxcross/SDK/MacOSX13.3.sdk \
  DEPLOYMENT_TARGET=11.0 \
  ARCH_COMPILER=oa64