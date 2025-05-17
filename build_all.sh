echo "This will start a build for all images, this takes a long time..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for directory in ./dockerfiles/*/; do
    version=$(basename "$directory") 
    for system in "$directory"*; do
        operating_system=$(basename "$system")
        ${SCRIPT_DIR}/build.sh $version $operating_system
        sleep 1 # Just to handle ctrl c exit
    done
done

