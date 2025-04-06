param (
    [string]$NUKEVERSION
)
$startPath = Get-Location

$answer = Read-Host "Starting build for: '$NUKEVERSION'."

Set-Location "dockerfiles\$NUKEVERSION\windows"
Write-Host "Creating image for Nuke version: $NUKEVERSION"
$SOURCES_DIR = "_nuke_sources"

$originalPath = Get-Location
New-Item -ItemType Directory -Force -Path $SOURCES_DIR

$dockerfilePath = Resolve-Path "Dockerfile"
$sourcesDirPath = Resolve-Path $SOURCES_DIR

..\..\..\scripts\nuke_source_from_dockerfile.ps1 $dockerfilePath $sourcesDirPath

Set-Location $originalPath


docker build . --tag nukedockerbuild:$NUKEVERSION-windows --build-arg="NUKE_SOURCE_FILES=$SOURCES_DIR"

Set-Location $startPath
