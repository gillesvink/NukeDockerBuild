#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path_to_dockerfile> <target_folder>"
    exit 1
fi

dockerfile_path="$1"
target_folder="$2"

url=$(grep "LABEL 'com.nukedockerbuild.nuke_source'" "$dockerfile_path" | awk -F"=" '{print $2}' | tr -d "'")
version=$(grep "LABEL 'com.nukedockerbuild.nuke_version'" "$dockerfile_path" | awk -F"=" '{print $2}' | tr -d "'")
if [ -z "$url" ]; then
    echo "Error: Label not found in the Dockerfile."
    exit 1
else
    echo "Process data from: $url"
fi

filename=$(basename "$url")
nuke_temp_files=/tmp/nuke_temp_files

mkdir -p ${target_folder}


echo "Download and extract Nuke in temp folder"
mkdir -p ${nuke_temp_files}
curl -o ${nuke_temp_files}/${filename} ${url}
unzip ${nuke_temp_files}/${filename} -d ${nuke_temp_files}

echo "Remove compressed Nuke"
rm ${nuke_temp_files}/${filename}

echo "Install Nuke to temp directory in Wine"

if (( $(echo "$version < 14.0" | bc -l) )); then
    wine ${nuke_temp_files}/${filename%.*}.exe  /S /ACCEPT-FOUNDRY-EULA /D=C:\\nuke_temp
else
    wine msiexec /i ${nuke_temp_files}/${filename%.*}.msi /qb /l log.txt INSTALL_ROOT=C:\\nuke_temp ACCEPT_FOUNDRY_EULA=ACCEPT
fi


echo "Moving to specified directory"
mv ~/.wine/drive_c/nuke_temp/* ${target_folder}/

echo "Keep only source files"
mkdir -p ${target_folder}/tests
cp -r ${target_folder}/Documentation/NDKExamples/examples/* ${target_folder}/tests

find "${target_folder}" -mindepth 1 -maxdepth 1 \
    ! -name "tests" \
    ! -name "cmake" \
    ! -name "include" \
    ! -name "source" \
    ! -name "*Fdk*" \
    ! -name "*Fn*" \
    ! -name "*DDI*" \
    ! -name "*RIPFramework*" \
    ! -name "glew32*" \
    ! -name "tbb*" \
    ! -name "*Ndk*" \
    -exec rm -rf {} +

echo "Clean nuke temp files"
rm -rf ${nuke_temp_files}
