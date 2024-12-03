> Ready to use build images to for Nuke plugins for Linux and Windows.

--- 
The images produced here will include everything you need to build Nuke plugins. This includes the compiler for C++ ([gcc-toolsets](https://access.redhat.com/documentation/en-us/red_hat_developer_toolset/12) on Linux, [Visual Studio](https://visualstudio.microsoft.com/downloads/) on Windows, [CMake](https://cmake.org/) and the Nuke files required to compile.)

These images are meant for both local development using development containers and deployment using CI/CD.


## How to use
Build the image you need locally. This can be done with the build.sh or build.ps1 scripts. Specify the Nuke version you need, and it will build the correct image to use. For example 15.1 is specified in the examples here:

### Linux
```bash
./build.sh 15.1
```

### Windows
```bash
./build.ps1 15.1
```

It is recommended to keep the builded images in your own registry, so you don't need to build each use.

## ⬆️ How is this updated? 
Since Nuke requires every minor release to be compiled natively, it needs to have a docker image as well for each minor version.

This is done in an automatic process to create the Dockerfiles whenever there is a new Nuke minor release. It uses the minor supported releases JSON from my other repo: [NukeVersionParser](https://github.com/gillesvink/NukeVersionParser).

This data is used once a day to check if there is anything new a new dockerfile will be created

## 📝 Quickstart 
First of all make sure you have Docker installed on your system. Guides can be found here at [Docker Install](https://docs.docker.com/engine/install/).
Once installed, you can test the docker image by running the command provided here. There might be some warnings of deprecation, that is because some source code in the examples uses deprecated functions.

### Windows docker requirements
Windows has some additional requirements to run this image. You need to have at least Windows 11 Pro or greater. Besides that, you need to 'switch to Windows containers' in the Docker Desktop application.

![Switch to Windows Containers](./resources/switch_to_windows.png)

Else it will use the Windows Subsystem for Linux (which is basically a virtualization of the Linux system, allowing you to even build Linux plugins on Windows.)

### Run tests locally
Beneath here are some quick tests to verify everything is working on your system. It should pass compiling (this is a test for a Nuke 15 image). It might take a while for the image to be downloaded
depending on your local internet connection.

#### Linux:
```bash
docker run --rm nukedockerbuild:15.0 bash -c "cd /usr/local/nuke_install/tests && cmake . -B build && cmake --build build"
```

#### Windows:
##### Powershell
```bash
docker run --rm `
    nukedockerbuild:13.0-windows-latest `
    powershell -Command "cd C:\nuke_install\tests ; `
    cmake . -DCMAKE_GENERATOR_PLATFORM=x64 -B build ; `
    cmake --build build --config Release"
```

### Building the current directory (that contains a CMakeLists file)
Note that you can change it to whatever Nuke version is available. In this example Nuke 15 is used.
#### Linux:
```bash
docker run --rm -v "$(pwd):/nuke_build_directory \
    nukedockerbuild:15.0-linux bash -c \
    "cmake . -B build && cmake --build build
```

#### Windows:
On Windows it is important that `--isolution=process` is set as it is mounting the directory, else there will be issues with cleaning files in the mounted directory. Also, for CMake building it requires the config to be specified for release using `--config Release`.
##### Powershell
```bash
docker run --rm --isolation=process `
    -v ${PWD}:C:\nuke_build_directory `
    nukedockerbuild:15.0-windows-latest powershell -Command `
    "cmake . -DCMAKE_GENERATOR_PLATFORM=x64 -B build ; `
    cmake --build build --config Release"
```

## ⚙️ Technical info
The images depend on the specs provided by the [NDK documentation](https://learn.foundry.com/nuke/developers/13.2/ndkdevguide/intro/pluginbuildinginstallation.html) and the [VFX reference platform](https://vfxplatform.com/).

Nuke will always be installed at `/usr/local/nuke_install` on Linux and `C:\nuke_install` on Windows. The entry directory if you execute this image will be `/nuke_build_directory` on Linux and `C:\nuke_build_directory` on Windows.

The image also has the `NUKE_VERSION` environment set, this will always contain the version that is available in the image. For example `15.0`

### Linux
All Linux images are based on Red Hat based images. This means [Rocky Linux](https://hub.docker.com/_/rockylinux) for Nuke 15+ and [CentOS](https://hub.docker.com/_/centos) for anything lower than 15. As [Foundry is using Rocky](https://learn.foundry.com/nuke/content/release_notes/15.0/nuke_15.0v1_releasenotes.html), I choose to stick to that as well. However it is basically identical to Alma.

### Windows
For Windows the [Server Core ltsc2022](https://hub.docker.com/_/microsoft-windows-servercore) image is used. Besides that, for package installation the [Chocolatey package registry](https://community.chocolatey.org/packages) is used to install both the VS Build Tools as well as CMake.


## ❤️ Thanks
Thanks to everyone who contributed anything to the images that are used in these dockerfiles and to the maintainers of all plugins used! Without all the open source code applications that are available this would never have been possible.

## ⚠️ Disclaimer
This project is an independent effort, not affiliated with or endorsed by Foundry. 
It provides Docker images for plugin building purposes. 
The terms "Nuke" and related trademarks are the property of Foundry, 
used here for descriptive purposes only. For official information and support, 
please refer to Foundry's [official website](https://www.foundry.com/).

By building this project, you agree on the [EULA](https://www.foundry.com/eula) provided by Foundry.
