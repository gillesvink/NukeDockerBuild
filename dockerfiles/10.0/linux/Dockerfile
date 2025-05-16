FROM centos:centos7.4.1708

LABEL 'org.opencontainers.version'=1.0
LABEL 'org.opencontainers.image.created'='2025-05-16'
LABEL 'org.opencontainers.image.description'='Ready to use image for building Nuke plugins.'
LABEL 'org.opencontainers.license'='MIT'
LABEL 'org.opencontainers.url'='https://codeberg.org/gillesvink/NukeDockerBuild'
LABEL 'com.nukedockerbuild.based_on'='centos:centos7.4.1708'
LABEL 'com.nukedockerbuild.operating_system'='linux'
LABEL 'com.nukedockerbuild.nuke_version'=10.0
LABEL 'com.nukedockerbuild.nuke_source'='https://thefoundry.s3.amazonaws.com/products/nuke/releases/10.0v6/Nuke10.0v6-linux-x86-release-64.tgz'

ARG NUKE_SOURCE_FILES

COPY $NUKE_SOURCE_FILES /usr/local/nuke_install

RUN ulimit -n 1024 \
  && sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/*.repo \
  && sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/*.repo \
  && sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/*.repo \
  && yum -y install centos-release-scl-rh  \
  && echo 'Use vault for SC packages as CentOS 7 reached EOL.' \
  && sed -i 's/7/7.4.1708/g; s|^#\s*\(baseurl=http://\)mirror|\1vault|g; /mirrorlist/d' /etc/yum.repos.d/CentOS-SCLo-*.repo \
  && yum -y install gcc gcc-c++ \
  && yum clean all \
  && rm -rf /var/cache/yum

RUN ulimit -n 1024 \
  && yum update -y \
  && yum -y install epel-release \
  && yum -y install mesa-libGLU-devel make \
  && cd /tmp/ \
  && curl -LO https://github.com/Kitware/CMake/releases/download/v3.27.7/cmake-3.27.7-linux-x86_64.sh \
  && chmod +x cmake-3.27.7-linux-x86_64.sh \
  && ./cmake-3.27.7-linux-x86_64.sh --prefix=/usr/local --skip-license \
  && rm cmake-3.27.7-linux-x86_64.sh \
  && yum clean all \
  && rm -rf /var/cache/yum

RUN ulimit -n 1024 \
  && yum update -y \
  && yum install -y autoconf curl-devel expat-devel gettext-devel openssl-devel zlib-devel perl-CPAN perl-devel xz \
  && cd /tmp \
  && curl -LO https://www.kernel.org/pub/software/scm/git/git-2.9.5.tar.xz \
  && tar xf git-2.9.5.tar.xz \
  && rm git-2.9.5.tar.xz \
  && cd git-2.9.5 \
  && make configure \
  && ./configure --prefix=/usr/local \
  && make all \
  && make install \
  && cd ../ \
  && rm -rf git-2.9.5 \
  && yum clean all \
  && rm -rf /var/cache/yum

WORKDIR /nuke_build_directory

ENV CMAKE_PREFIX_PATH=/usr/local/nuke_install
ENV NUKE_VERSION=10.0