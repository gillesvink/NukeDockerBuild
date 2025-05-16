#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <nuke-version> <windows/linux>"
    exit 1
fi

NUKEVERSION="$1"
OPERATING_SYSTEM="$2"
MAIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKERFILE_DIR=${MAIN_DIR}/dockerfiles/${NUKEVERSION}/${OPERATING_SYSTEM}

apk add curl bc

if [ "$OPERATING_SYSTEM" == "windows" ]; then
    if (( $(echo "$NUKEVERSION < 13.0" | bc -l) )); then
        echo "Nuke versions lower than 13.0 are not supported on Windows."
        exit 1
    fi
    apk add wine
    cp ${MAIN_DIR}/dependencies/windows/toolchain.cmake $DOCKERFILE_DIR
fi

if (( $(echo "$NUKEVERSION < 11.0" | bc -l) )); then
    apk add unzip
fi


cd ${MAIN_DIR}/dockerfiles/${NUKEVERSION}/${OPERATING_SYSTEM}
echo "Creating image for Nuke version: ${NUKEVERSION}:${OPERATING_SYSTEM}"
SOURCES_DIR="_nuke_sources"

mkdir -p ${SOURCES_DIR}
${MAIN_DIR}/scripts/get_nuke_${OPERATING_SYSTEM}.sh Dockerfile ${SOURCES_DIR}

if [ -d "cmake" ]; then
    echo "Found cmake folder for backwards compatibility"
    cp -r cmake $SOURCES_DIR
fi

if [ -d "tests" ]; then
    echo "Found test folder for backwards compatibility"
    cp -r tests $SOURCES_DIR
fi

docker buildx build \
    -t nukedockerbuild:$NUKEVERSION-${OPERATING_SYSTEM} \
    --build-arg NUKE_SOURCE_FILES=$SOURCES_DIR \
    .

docker save -o /build/nukedockerbuild:$NUKEVERSION-${OPERATING_SYSTEM}.tar nukedockerbuild:$NUKEVERSION-${OPERATING_SYSTEM}
chmod 777 /build/nukedockerbuild:$NUKEVERSION-${OPERATING_SYSTEM}.tar
