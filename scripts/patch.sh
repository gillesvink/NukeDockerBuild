#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <nuke_source_files>"
    exit 1
fi

source_files="${1}"

echo "Patching source files: ${1}"