FROM mcr.microsoft.com/windows/servercore:ltsc2022

LABEL 'org.opencontainers.version'=0.2
LABEL 'org.opencontainers.image.created'='2024-01-10'
LABEL 'org.opencontainers.image.authors'='gilles@vinkvfx.com'
LABEL 'org.opencontainers.image.description'='Ready to use Docker image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://github.com/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='mcr.microsoft.com/windows/servercore:ltsc2022'
LABEL 'com.nukedockerbuild.operating_system'='windows'
LABEL 'com.nukedockerbuild.nuke_version'=13.0
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/13.0v10/Nuke13.0v10-win-x86_64.zip'

ARG NUKE_SOURCE_FILES
COPY $NUKE_SOURCE_FILES C:\\nuke_install
COPY cmake C:\\nuke_install\\cmake

RUN powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin" \
  && choco install cmake --installargs 'ADD_CMAKE_TO_PATH=System' -y \
  && choco install visualstudio2017buildtools -y \
  && choco install visualstudio2017-workload-vctools --package-parameters '--includeRecommended' -y \
  && powershell -Command "Remove-Item -Path \"$env:TEMP\*\" -Force -Recurse" \
  && powershell -Command "Remove-Item -Path 'C:\ProgramData\Package Cache\*' -Force -Recurse"

WORKDIR C:\\nuke_build_directory

ENV CMAKE_PREFIX_PATH=C:\\nuke_install