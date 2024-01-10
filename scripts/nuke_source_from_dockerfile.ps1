# Simple script to retrieve Nuke source files from provided Dockerfile

<#
    This is meant as a workaround for the 14gb limit in the CI/CD machines.
    So we can pass the extracted source files as an argument instead of downloading and building
    at the same time. Otherwise, this could be easily done within the Dockerfile itself.
#>

param(
    [string]$dockerfilePath,
    [string]$targetFolder
)


$url = (Get-Content $dockerfilePath | Select-String "LABEL 'com.nukedockerbuild.nuke_source'" | ForEach-Object { $_ -replace ".*= '", "" -replace "'" }).Trim()
if (-not $url) {
    Write-Host "Error: Label not found in the Dockerfile."
    exit 1
} else {
    $url = $url -replace '^.*='
    Write-Host "Process data from: $url"
}

$filename = [System.IO.Path]::GetFileName($url)
$nukeTempFiles = Join-Path $env:TEMP "nuke_temp_files"
Write-Host "Temp files dir: $nukeTempFiles"

$version = [regex]::Match($url, '(?<=releases\/)\d+(\.\d+)').Value
$version = [float]$version

Write-Host "Download and extract Nuke in temp folder"
New-Item -ItemType Directory -Force -Path $nukeTempFiles | Out-Null
curl.exe -o (Join-Path $nukeTempFiles $filename) $url
tar -xf (Join-Path $nukeTempFiles $filename) -C $nukeTempFiles

Write-Host "Remove compressed Nuke"
Remove-Item -Path (Join-Path $nukeTempFiles $filename) -Force

Write-Host "Install Nuke to $targetFolder"
if ($version -lt 14.0) {
    $installer = (Join-Path $nukeTempFiles ($filename -replace '\.zip', '.exe'))
    Write-Host "Using older installation instructions"
    Start-Process -FilePath "$installer" -ArgumentList "/S /ACCEPT-FOUNDRY-EULA /D=$targetFolder" -Wait
} else {
    $installer = (Join-Path $nukeTempFiles ($filename -replace '\.zip', '.msi'))
    Write-Host "Using new installation instructions"
    Start-Process -FilePath "msiexec.exe" -ArgumentList "/i $installer ACCEPT_FOUNDRY_EULA=ACCEPT INSTALL_ROOT=`$targetFolder` /qb /l log.txt" -Wait
}

Write-Host "Keep only source files"
New-Item -ItemType Directory -Force -Path (Join-Path $targetFolder "tests") | Out-Null
Copy-Item -Path (Join-Path $targetFolder "Documentation\NDKExamples\examples\*") -Destination (Join-Path $targetFolder "tests") -Recurse
Get-ChildItem -Path $targetFolder -Exclude "tests", "cmake", "include", "source", "*Fdk*", "*Fn*", "*DDI*" | Remove-Item -Recurse -Force

Write-Host "Clean nuke temp files"
Remove-Item -Path $nukeTempFiles -Recurse -Force
