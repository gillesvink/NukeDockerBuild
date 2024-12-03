param (
    [string]$NUKEVERSION
)

$answer = Read-Host "Is the Nuke version correct: '$NUKEVERSION'. It can be for example 13.2, it has to be in this precise format (y/n)"

if ($answer -match '^[Yy]$') {
    Write-Host "Continuing installation..."
} else {
    Write-Host "Please change the input"
    exit 1
}

Set-Location "dockerfiles\$NUKEVERSION\linux"
Write-Host "Creating image for Nuke version: $NUKEVERSION"
$SOURCES_DIR = "_nuke_sources"

New-Item -ItemType Directory -Force -Path $SOURCES_DIR

& "../../../scripts/nuke_source_from_dockerfile_windows.ps1" "Dockerfile" $SOURCES_DIR

docker buildx build `
    -t "nukedockerbuild:$NUKEVERSION-linux-latest" `
    --build-arg "NUKE_SOURCE_FILES=$SOURCES_DIR" `
    .
