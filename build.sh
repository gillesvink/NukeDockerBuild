#!/bin/bash

NUKEVERSION="$1"

read -p "Is the Nuke version correct: '$NUKEVERSION'. It can be for example 13.2, it has to be in this precise format (y/n): " answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Continuing installation..."
else
    echo "Please change the input"
    exit 1
fi

cd dockerfiles/$NUKEVERSION/linux
echo "Creating image for Nuke version: $NUKEVERSION"
SOURCES_DIR="_nuke_sources"

mkdir -p $SOURCES_DIR
../../../scripts/nuke_source_from_dockerfile_linux.sh Dockerfile $SOURCES_DIR

docker buildx build \
    -t nukedockerbuild:$NUKEVERSION-linux-latest \
    --build-arg NUKE_SOURCE_FILES=$SOURCES_DIR \
    .

