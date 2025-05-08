#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path_to_dockerfile> <target_folder>"
    exit 1
fi

dockerfile_path="$1"
target_folder="$2"

url=$(grep "LABEL 'com.nukedockerbuild.nuke_source'" "$dockerfile_path" | awk -F"=" '{print $2}' | tr -d "'")
if [ -z "$url" ]; then
    echo "Error: Label not found in the Dockerfile."
    exit 1
else
    echo "Process data from: $url"
fi

filename=$(basename "$url")
nuke_temp_files=/tmp/nuke_temp_files

echo "Download and extract Nuke in temp folder"
mkdir ${nuke_temp_files}
curl -o ${nuke_temp_files}/${filename} ${url}
tar zxvf ${nuke_temp_files}/${filename} -C ${nuke_temp_files}

echo "Remove compressed Nuke"
rm ${nuke_temp_files}/${filename}

echo "Install Nuke to ${target_folder}"
chmod +x ${nuke_temp_files}/${filename%.*}.run
${nuke_temp_files}/${filename%.*}.run --accept-foundry-eula --prefix=${target_folder} --exclude-subdir

echo "Keep only source files"
mkdir ${target_folder}/tests
cp -r ${target_folder}/Documentation/NDKExamples/examples/* ${target_folder}/tests

find ${target_folder} -mindepth 1 -maxdepth 1 ! -name "tests" ! -name "cmake" ! -name "include" ! -name "*Fdk*" ! -name "*Fn*" ! -name "*Ndk*" ! -name "*DDI*" ! -name "source" -exec rm -rf {} \;

echo "Clean nuke temp files"
rm -rf ${nuke_temp_files}
