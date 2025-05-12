#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <nuke-version> <windows/linux>"
    exit 1
fi

NUKEVERSION="$1"
OPERATING_SYSTEM="$2"

echo "Starting build for: '${NUKEVERSION}'."

DOCKERFILE_DIR=dockerfiles/${NUKEVERSION}/${OPERATING_SYSTEM}

if [ "$OPERATING_SYSTEM" == "windows" ]; then
    cp dependencies/windows/toolchain.cmake $DOCKERFILE_DIR
fi


cd dockerfiles/${NUKEVERSION}/${OPERATING_SYSTEM}
echo "Creating image for Nuke version: ${NUKEVERSION}:${OPERATING_SYSTEM}"
SOURCES_DIR="_nuke_sources"

mkdir -p ${SOURCES_DIR}
../../../scripts/get_nuke_${OPERATING_SYSTEM}.sh Dockerfile ${SOURCES_DIR}

if [ -d "cmake" ]; then
    echo "Found cmake folder for backwards compatibility"
    cp -r cmake $SOURCES_DIR
fi

docker buildx build \
    -t nukedockerbuild:$NUKEVERSION-${OPERATING_SYSTEM} \
    --build-arg NUKE_SOURCE_FILES=$SOURCES_DIR \
    .

