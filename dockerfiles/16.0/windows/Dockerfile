FROM ubuntu:22.04

LABEL 'org.opencontainers.version'=2.0
LABEL 'org.opencontainers.image.created'='2025-05-08'
LABEL 'org.opencontainers.image.description'='Ready to use image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://codeberg.org/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='ubuntu:22.04'
LABEL 'com.nukedockerbuild.operating_system'='windows'
LABEL 'com.nukedockerbuild.nuke_version'=16.0
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/16.0v2/Nuke16.0v2-win-x86_64.zip'

ARG NUKE_SOURCE_FILES
ARG TOOLCHAIN

COPY $NUKE_SOURCE_FILES /usr/local/nuke_install
COPY $TOOLCHAIN /nukedockerbuild/

RUN apt-get update \
  && apt-get install wine64 python3 msitools ca-certificates git wget ninja-build winbind -y  \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/* \
  && wget https://github.com/Kitware/CMake/releases/download/v3.29.3/cmake-3.29.3-linux-x86_64.sh \
  && chmod +x cmake-3.29.3-linux-x86_64.sh \
  && ./cmake-3.29.3-linux-x86_64.sh --prefix=/usr/local --skip-license \
  && rm cmake-3.29.3-linux-x86_64.sh

RUN $(command -v wine64 || command -v wine || false) wineboot --init \
  && while pgrep wineserver > /dev/null; do sleep 1; done

RUN cd ~/ \
  && git clone https://github.com/mstorsjo/msvc-wine.git \
  && cd msvc-wine \
  && git checkout 44dc13b5e62ecc2373fbe7e4727a525001f403f4 \
  && PYTHONUNBUFFERED=1 ./vsdownload.py --major 17 --accept-license --dest /opt/msvc \
  && ./install.sh /opt/msvc \
  && mv ./msvcenv-native.sh /opt/msvc \
  && cd ../ && rm -rf ./msvc-wine \
  && bash -c 'export BIN=/opt/msvc/bin/x64/ \
  && . /opt/msvc/msvcenv-native.sh \
  && MSVCDIR=$(. "${BIN}msvcenv.sh" && echo $MSVCDIR) \
  && MSVCDIR=${MSVCDIR//\\\\//} \
  && MSVCDIR=${MSVCDIR#z:} \
  && echo "export BIN=${BIN}" >> /etc/bashrc \
  && echo "export MSVCDIR=$MSVCDIR" >> /etc/bashrc \
  && echo "export CC=${BIN}cl" >> /etc/basbashrc \
  && echo "export CXX=${BIN}cl" >> /etc/bashrc \
  && echo "export RC=${BIN}rc" >> /etc/bashrc \
  && echo "source /opt/msvc/msvcenv-native.sh" >> /etc/bashrc'

WORKDIR /nuke_build_directory

ENV CMAKE_PREFIX_PATH=/usr/local/nuke_install \
  PATH=/opt/msvc/bin/x64:$PATH \
  GLOBAL_TOOLCHAIN=/nukedockerbuild/toolchain.cmake
ENV NUKE_VERSION=16.0