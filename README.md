> Ready to use build images for Nuke plugins for Linux and Windows.

--- 
The images produced here will include everything you need to build Nuke plugins. This includes the compiler for C++ ([gcc-toolsets](https://access.redhat.com/documentation/en-us/red_hat_developer_toolset/12) on Linux, [Visual Studio](https://visualstudio.microsoft.com/downloads/) on Windows, [CMake](https://cmake.org/) and the Nuke files required to compile.)

These images are meant for both local development using development containers and deployment using CI/CD.


## How to use
Build the image you need locally. This can be done with the `build.sh` script. Specify the Nuke version you need, and it will build the correct image to use. For example 15.1 is specified in the examples here:

> [!TIP]
> For security it is recommended to use Podman, as these images do not require any root privilege.

It is build within a separate dind container, and then copied over to the host. This makes it possible to build images with just Docker or Podman installed. All necessary dependencies will be installed automatically within the dind/podman container.

### Linux
```bash
./build.sh 15.1 linux
./build.sh 15.1 linux --podman # for podman build
```

### Windows
Please note that it takes some time to run. It will show some Wine errors due to no display being available in the containerized build. This is fine however. (The entire build takes around ~15 minutes on my machine)
```bash
./build.sh 15.1 windows
./build.sh 15.1 windows --podman # for podman build

```

It is recommended to push the built images to your own registry, so you don't need to build each use.

## ⬆️ How is this updated? 
Since Nuke requires every minor release to be compiled natively, it needs to have an image as well for each minor version.

This is done in an automatic process to create the Dockerfiles whenever there is a new Nuke minor release. It uses the minor supported releases JSON from my other repo: [NukeVersionParser](https://codeberg.org/gillesvink/NukeVersionParser).

This data is used once a day to check if there is anything new a new dockerfile will be created

## 📝 Quickstart 
First of all make sure you have Docker or Podman installed on your system. Guides can be found here at [Docker Install](https://docs.docker.com/engine/install/) or at [Podman Install](https://podman.io/docs/installation).
Once installed, you can test the image by running the command provided here. There might be some warnings of deprecation, that is because some source code in the examples uses deprecated functions.

### Run tests locally
Beneath here are some quick tests to verify everything is working on your system. It should pass compiling (this is a test for a Nuke 15 image). It might take a while for the image to be downloaded
depending on your local internet connection.

#### Linux:
```bash
./build.sh 15.1 linux
docker run --rm nukedockerbuild:15.1-linux bash -c "cd /usr/local/nuke_install/tests && cmake . -B build && cmake --build build"
```

#### Windows:
```bash
./build.sh 15.1 windows
docker run --rm nukedockerbuild:16.0-windows bash -c "
    cd /usr/local/nuke_install/tests && \
    cmake . \
        -GNinja \
        -DCMAKE_SYSTEM_NAME=Windows \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_TOOLCHAIN_FILE=$GLOBAL_TOOLCHAIN \
        -B build && \
    cmake --build build
"
```

### Building the current directory (that contains a CMakeLists file)
Note that you can change it to whatever Nuke version is available. In this example Nuke 15 is used.
#### Linux:
```bash
docker run --rm -v "$(pwd):/nuke_build_directory \
    nukedockerbuild:15.0-linux bash -c \
    "cmake . -B build && cmake --build build
```

## ⚙️ Technical info
The images depend on the specs provided by the [NDK documentation](https://learn.foundry.com/nuke/developers/13.2/ndkdevguide/intro/pluginbuildinginstallation.html) and the [VFX reference platform](https://vfxplatform.com/).

Nuke will always be installed at `/usr/local/nuke_install` The entry directory if you execute this image will be `/nuke_build_directory`.

The image also has the `NUKE_VERSION` environment set, this will always contain the version that is available in the image. For example `15.0`

### Linux
All Linux images are based on Red Hat based images. This means [Rocky Linux](https://hub.docker.com/_/rockylinux) for Nuke 15+ and [manylinux2014](https://quay.io/repository/pypa/manylinux2014_x86_64?tab=tags) for anything lower than 15. As [Foundry is using Rocky](https://learn.foundry.com/nuke/content/release_notes/15.0/nuke_15.0v1_releasenotes.html), I choose to stick to that as well. However it is basically identical to Alma.

### Windows
Windows images are based on Debian Bookworm. They use the [wine-msvc](https://github.com/mstorsjo/msvc-wine) project to make cross compilation possible. As they mention:
> This downloads and unpacks the necessary Visual Studio components using the same installer manifests as Visual Studio 2017/2019's installer uses. Downloading and installing it requires accepting the license, available at https://go.microsoft.com/fwlink/?LinkId=2086102 for the currently latest version.

So be sure to read that before using this project.

## ❤️ Thanks
Thanks to everyone who contributed anything to the images that are used in these dockerfiles and to the maintainers of all plugins used! Without all the open source code applications that are available this would never have been possible.

## ⚠️ Disclaimer
This project is an independent effort, not affiliated with or endorsed by Foundry. 
It provides Docker images for plugin building purposes. 
The terms "Nuke" and related trademarks are the property of Foundry, 
used here for descriptive purposes only. For official information and support, 
please refer to Foundry's [official website](https://www.foundry.com/).

By building this project, you agree on the [EULA](https://www.foundry.com/eula) provided by Foundry.