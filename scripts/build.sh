#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <nuke-version> <windows/linux> [optional: --podman]"
    exit 1
fi

NUKEVERSION="$1"
OPERATING_SYSTEM="$2"
USE_PODMAN=false

if [ "$#" -eq 3 ] && [ "$3" == "--podman" ]; then
    USE_PODMAN=true
fi

MAIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKERFILE_DIR=${MAIN_DIR}/dockerfiles/${NUKEVERSION}/${OPERATING_SYSTEM}

if $USE_PODMAN; then
    dnf install -y curl bc
else
    apk add curl bc
fi

if [ "$OPERATING_SYSTEM" == "windows" ]; then
    if (( $(echo "$NUKEVERSION < 12.0" | bc -l) )); then
        echo "Nuke versions lower than 12.0 are not supported on Windows."
        exit 1
    fi

    if $USE_PODMAN; then
        dnf install wine -y
    else
        echo http://dl-cdn.alpinelinux.org/alpine/edge/community >> /etc/apk/repositories
        apk update
        apk add wine
    fi

    wineboot --init

    cp ${MAIN_DIR}/dependencies/windows/toolchain.cmake ${DOCKERFILE_DIR}
fi

if (( $(echo "${NUKEVERSION} < 11.0" | bc -l) )); then
    if $USE_PODMAN; then
        dnf install -y unzip
    else
        apk add unzip
    fi
fi

cd ${MAIN_DIR}/dockerfiles/${NUKEVERSION}/${OPERATING_SYSTEM} || exit 1
echo "Creating image for Nuke version: ${NUKEVERSION}:${OPERATING_SYSTEM}"
SOURCES_DIR="_nuke_sources"

mkdir -p ${SOURCES_DIR}
${MAIN_DIR}/scripts/get_nuke_${OPERATING_SYSTEM}.sh Dockerfile ${SOURCES_DIR}

if [ -d "cmake" ]; then
    echo "Found cmake folder for backwards compatibility"
    cp -r cmake ${SOURCES_DIR}
fi

if [ -d "tests" ]; then
    echo "Found test folder for backwards compatibility"
    cp -r tests ${SOURCES_DIR}
fi

if $USE_PODMAN; then
    podman build \
        -t nukedockerbuild:${NUKEVERSION}-${OPERATING_SYSTEM} \
        --build-arg NUKE_SOURCE_FILES=${SOURCES_DIR} \
        .

    podman save -o /build/nukedockerbuild-${NUKEVERSION}-${OPERATING_SYSTEM}.tar nukedockerbuild:${NUKEVERSION}-${OPERATING_SYSTEM}
else
    docker buildx build \
        -t nukedockerbuild:${NUKEVERSION}-${OPERATING_SYSTEM} \
        --build-arg NUKE_SOURCE_FILES=${SOURCES_DIR} \
        .

    docker save -o /build/nukedockerbuild-${NUKEVERSION}-${OPERATING_SYSTEM}.tar nukedockerbuild:${NUKEVERSION}-${OPERATING_SYSTEM}
    chmod 777 /build/nukedockerbuild:${NUKEVERSION}-${OPERATING_SYSTEM}.tar
fi

