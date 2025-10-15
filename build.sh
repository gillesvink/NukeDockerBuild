#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <nuke-version> <windows/linux> [optional: --podman, --skip-load]"
    exit 1
fi

NUKEVERSION="$1"
OPERATING_SYSTEM="$2"
USE_PODMAN=false
SKIP_LOAD=false

for arg in "${@:3}"; do
    case "$arg" in
        --podman) USE_PODMAN=true ;;
        --skip-load) SKIP_LOAD=true ;;
    esac
done


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if $USE_PODMAN; then
    command -v podman &> /dev/null || { echo "Podman not installed. Please install that first."; exit 1; }
else
    command -v docker &> /dev/null || { echo "Docker not installed. Please install that first."; exit 1; }
fi

echo "Starting build for: '${NUKEVERSION}'."
mkdir -p build

if $USE_PODMAN; then
    podman run \
        -v "${SCRIPT_DIR}:/nukedockerbuild" \
        -v ${SCRIPT_DIR}/build:/build \
        --rm \
        --cap-add=sys_admin,mknod \
        --device=/dev/fuse \
        --security-opt label=disable \
        quay.io/podman/stable:latest \
        bash -c "/nukedockerbuild/scripts/build.sh ${NUKEVERSION} ${OPERATING_SYSTEM} --podman"

    if ! $SKIP_LOAD; then
        podman load -i ${SCRIPT_DIR}/build/nukedockerbuild-${NUKEVERSION}-${OPERATING_SYSTEM}.tar
        rm -rf /build/nukedockerbuild-${NUKEVERSION}-${OPERATING_SYSTEM}.tar
    fi

else
    docker run \
        -v "${SCRIPT_DIR}:/nukedockerbuild" \
        -v ${SCRIPT_DIR}/build:/build \
        -v /var/run/docker.sock:/var/run/docker.sock \
        --rm \
        docker.io/docker:dind \
        sh -c "apk add --no-cache bash && \
        /nukedockerbuild/scripts/build.sh ${NUKEVERSION} ${OPERATING_SYSTEM}"

    if ! $SKIP_LOAD; then
        docker load -i ${SCRIPT_DIR}/build/nukedockerbuild:${NUKEVERSION}-${OPERATING_SYSTEM}.tar
        docker run \
            -v "${SCRIPT_DIR}/build:/build" \
            --rm \
            docker.io/docker:dind \
            sh -c "rm -rf /build/nukedockerbuild:${NUKEVERSION}-${OPERATING_SYSTEM}.tar"
    fi
fi
