#!/bin/bash

: <<'END_COMMENT'
 Simple script to retrieve Nuke source files from provided Dockerfile

This is meant as a workaround for the 14gb limit in the CI/CD machines.
So we can pass the extracted source files as an argument instead of downloading and building
at the same time. Otherwise this could be easily done within the Dockerfile itself.

END_COMMENT

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
nuke_temp_files=/$TMPDIR/nuke_temp_files

echo "Download and extract Nuke in temp folder"
mkdir ${nuke_temp_files}
curl -o ${nuke_temp_files}/${filename} ${url}
tar zxvf ${nuke_temp_files}/${filename} -C ${nuke_temp_files}

echo "Mount and convert ${nuke_temp_files}/${filename}"
hdiutil convert "${nuke_temp_files}/${filename}" -format UDTO -o "${nuke_temp_files}/converted.cdr"
hdiutil attach "${nuke_temp_files}/converted.cdr"

echo "Copying files from dmg"
nuke_name=${filename%%-*}
cd /Volumes/${filename%.*}/${nuke_name}
mkdir ${target_folder}/tests
cp -r Documentation/NDKExamples/examples/* ${target_folder}/tests
cp -r ${nuke_name}.app/Contents/MacOS/* ${target_folder}

echo "Keep only source files"
find ${target_folder} -mindepth 1 -maxdepth 1 ! -name "tests" ! -name "cmake" ! -name "include" ! -name "*Fdk*" ! -name "*Fn*" ! -name "*Ndk*" ! -name "*DDI*" ! -name "source" -exec rm -rf {} \;

echo "Clean nuke temp files"
rm -rf ${nuke_temp_files}
