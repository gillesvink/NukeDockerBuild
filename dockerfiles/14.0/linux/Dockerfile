FROM centos:centos7.9.2009

LABEL 'org.opencontainers.version'=1.0
LABEL 'org.opencontainers.image.created'='2024-01-15'
LABEL 'org.opencontainers.image.authors'='gilles@vinkvfx.com'
LABEL 'org.opencontainers.image.description'='Ready to use Docker image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://github.com/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='centos:centos7.9.2009'
LABEL 'com.nukedockerbuild.operating_system'='linux'
LABEL 'com.nukedockerbuild.nuke_version'=14.0
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/14.0v6/Nuke14.0v6-linux-x86_64.tgz'

ARG NUKE_SOURCE_FILES
COPY $NUKE_SOURCE_FILES /usr/local/nuke_install

RUN echo 'Installing required packages.' \
  && ulimit -n 1024 \
  && yum -y install epel-release \
  && yum -y install centos-release-scl \
  && yum -y install devtoolset-9 \
  && yum -y install cmake3 \
  && yum -y install mesa-libGLU-devel

RUN echo 'Setting devtoolset to devtoolset-9.' \
  && echo 'unset BASH_ENV PROMPT_COMMAND ENV && source scl_source enable devtoolset-9' >> /usr/bin/scl_enable \
  && echo 'source scl_source enable devtoolset-9' >> /etc/bashrc \
  && chmod +x /usr/bin/scl_enable

WORKDIR /nuke_build_directory

ENV CMAKE_PREFIX_PATH=/usr/local/nuke_install \
  BASH_ENV=/usr/bin/scl_enable \
  ENV=/usr/bin/scl_enable \
  PROMPT_COMMAND=/usr/bin/scl_enable
ENV NUKE_VERSION=14.0