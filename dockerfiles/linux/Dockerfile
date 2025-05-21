FROM docker.io/debian:bookworm

LABEL 'org.opencontainers.version'=2.0
LABEL 'org.opencontainers.image.description'='Ready to use image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://codeberg.org/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='docker.io/debian:bookworm'
LABEL 'com.nukedockerbuild.operating_system'='linux'
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/14.0v8/Nuke14.0v8-linux-x86_64.tgz'

ARG NUKE_SOURCE_FILES
ARG CXXFLAGS
ARG NUKE_VERSION


RUN apt-get update install mesa-libGLU-devel curl bin-utils -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

RUN cd /root && \
    curl -LO https://ziglang.org/download/0.14.0/zig-linux-x86_64-0.14.0.tar.xz && \
    tar xf zig-linux-x86_64-0.14.0.tar.xz  && \
    echo 'export PATH="$HOME/zig-linux-x86_64-0.14.0:$PATH"' >> ~/.bashrc

WORKDIR /build

COPY $NUKE_SOURCE_FILES /usr/local/nuke_install

ENV CMAKE_PREFIX_PATH=/usr/local/nuke_install \
    CXXFLAGS=${CXXFLAGS}
ENV NUKE_VERSION=${NUKE_VERSION}