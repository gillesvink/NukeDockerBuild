#!/bin/bash

NUKEVERSION="$1"

echo "Starting build for: '$NUKEVERSION'."

cd dockerfiles/$NUKEVERSION/linux
echo "Creating image for Nuke version: $NUKEVERSION"
SOURCES_DIR="_nuke_sources"

mkdir -p $SOURCES_DIR
../../../scripts/nuke_source_from_dockerfile_linux.sh Dockerfile $SOURCES_DIR

if [ -d "cmake" ]; then
    echo "Found cmake folder for backwards compatibility"
    cp -r cmake $SOURCES_DIR
fi

docker buildx build \
    -t nukedockerbuild:$NUKEVERSION-linux \
    --build-arg NUKE_SOURCE_FILES=$SOURCES_DIR \
    .

