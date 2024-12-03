FROM mcr.microsoft.com/windows/servercore:ltsc2022

LABEL 'org.opencontainers.version'=1.0
LABEL 'org.opencontainers.image.created'='2024-12-03'
LABEL 'org.opencontainers.image.description'='Ready to use Image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://github.com/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='mcr.microsoft.com/windows/servercore:ltsc2022'
LABEL 'com.nukedockerbuild.operating_system'='windows'
LABEL 'com.nukedockerbuild.nuke_version'=15.1
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.1v4/Nuke15.1v4-win-x86_64.zip'

ARG NUKE_SOURCE_FILES

COPY $NUKE_SOURCE_FILES C:\\nuke_install

RUN powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin" \
  && choco install cmake --installargs 'ADD_CMAKE_TO_PATH=System' -y \
  && choco install visualstudio2022buildtools -y \
  && choco install visualstudio2022-workload-vctools --package-parameters '--includeRecommended' -y \
  && powershell -Command "Remove-Item -Path \"$env:TEMP\*\" -Force -Recurse" \
  && powershell -Command "Remove-Item -Path 'C:\ProgramData\Package Cache\*' -Force -Recurse"

WORKDIR C:\\nuke_build_directory

ENV CMAKE_PREFIX_PATH=C:\\nuke_install
ENV NUKE_VERSION=15.1