#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <nuke-version> <windows/linux>"
    exit 1
fi

NUKEVERSION="$1"
OPERATING_SYSTEM="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v docker &> /dev/null || { echo "Docker not installed. Please install that first."; exit 1; }

echo "Starting build for: '${NUKEVERSION}'."
mkdir -p build

docker run \
    -v "${SCRIPT_DIR}:/nukedockerbuild" \
    -v ${SCRIPT_DIR}/build:/build \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --rm \
    docker.io/docker:dind \
    sh -c "apk add --no-cache bash && \
    /nukedockerbuild/scripts/build.sh ${NUKEVERSION} ${OPERATING_SYSTEM}"

docker load -i ${SCRIPT_DIR}/build/nukedockerbuild:${NUKEVERSION}-${OPERATING_SYSTEM}.tar

docker run \
    -v "${SCRIPT_DIR}/build:/build" \
    --rm \
    docker.io/docker:dind \
    sh -c "rm -rf /build/nukedockerbuild:${NUKEVERSION}-${OPERATING_SYSTEM}.tar"
