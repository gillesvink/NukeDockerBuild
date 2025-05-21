#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <nuke_version> <target_folder>"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


version=$(echo "$1" | sed -E 's/^([0-9]+\.[0-9]+).*/\1/')
major=$(echo "${version}" | awk -F '.' '{print $1}')
target_folder="$2"

minor_releases_url=https://codeberg.org/gillesvink/NukeVersionParser/raw/branch/main/nuke-minor-releases.json

url=$(curl -s "${minor_releases_url}" | jq -r --arg prefix "$version" --arg major "$major" '
  .[$major] | to_entries[] | select(.key | startswith($prefix)) | .value.installer.linux_x86_64
')


if [ -z "$url" ]; then
    echo "No version found for: '${version}'. Is it actually an existing version?"
    exit 1
else
    echo "Downloading from: $url"
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
if (( $(echo "$version < 12.0" | bc -l) )); then
    unzip ${nuke_temp_files}/${filename%.*}-installer -d ${target_folder}
else
    chmod +x ${nuke_temp_files}/${filename%.*}.run
    ${nuke_temp_files}/${filename%.*}.run --accept-foundry-eula --prefix=${target_folder} --exclude-subdir
fi

echo "Keep only source files"
mkdir -p ${target_folder}/tests
if (( $(echo "$version < 12.0" | bc -l) )); then
    cp -r ${target_folder}/Documentation/NDK/examples/* ${target_folder}/tests
else
    cp -r ${target_folder}/Documentation/NDKExamples/examples/* ${target_folder}/tests
fi

find ${target_folder} -mindepth 1 -maxdepth 1 ! -name "tests" ! -name "cmake" ! -name "include" ! -name "*Fdk*" ! -name "*Fn*" ! -name "*Ndk*" ! -name "*DDI*" ! -name "source" -exec rm -rf {} \;

echo "Clean nuke temp files"
rm -rf ${nuke_temp_files}

${SCRIPT_DIR}/patch.sh ${target_folder}