# 🐬 NukeDockerBuild 
> Ready to use Docker containers to build Nuke plugins for Linux and Windows.


The images produced here will include everything you need to build Nuke plugins. This includes the compiler for C++, CMake and the Nuke files required to compile.

It is mostly meant for automatic deployment using CI/CD. However, it can also be used locally to quickly compile plugins without the need to install anything (except Docker itself 😉).

## 🏷 Tags
Current images that are available to use. Note that there also is the locked tag available. This image will never be updated. The default latest tag will possibly be updated, making sure you are using the latest things added automatically.

The :latest tag is missing on purpose, as this does not make any sense in this scenario. A nuke version needs to be chosen to compile to, thus needing to specify the tag which image to use for which Nuke version.

TODO: Data to be added

| Tag | Locked Tag | Nuke Version | Target OS | Upstream Image | Image Size |
|-----|------------|--------------|------------------|-------|------|
|     |            |              |                  |       |      |
|     |            |              |                  |       |      |
|     |            |              |                  |       |      |


## ⬆️ How is this updated? 
Since Nuke requires every minor release to be compiled natively, it needs to have a docker image as well for each minor version.

This is done in an automatic process to create the Dockerfiles whenever there is a new Nuke minor release. It uses the minor supported releases JSON from my other repo: [NukeVersionParser](https://github.com/gillesvink/NukeVersionParser).

This data is used once a day to check if there is anything new, and if there is anything new, a new Docker image will be build using the CI/CD process.

## 📝 Quickstart 
First of all make sure you have Docker installed on your system. Guides can be found here at [Docker Install](https://docs.docker.com/engine/install/).

Once installed, you can test the docker image by running the command provided here. There might be some warnings, but that is normal. It should not crash however.

Beneath here are some quick tests to verify everything is working on your system. It should pass compiling (this is a test for a Nuke 15 image). 

### Linux:
```bash
docker run --rm -it ghcr.io/gillesvink/nukedockerbuild:15.0-linux-latest bash -c "cd /nuke_tests && cmake . -B build && cmake --build build"
```
### Windows:
```bash
docker run --rm -it ghcr.io/gillesvink/nukedockerbuild:15.0-windows-latest Powershell -Command "cd C:\nuke_tests && cmake . -B build && cmake --build build"
```


## 🍎 Why no MacOS support? 
I wish... However, Apple does not support containerized applications as its missing good handling for chroot. The good news is, there currently is being done active work by the community to create a dockerized Mac OS image. Until that's solid, that will of course be supported here as well.

## Image size
Thats an issue of this approach, there are quite some files necessary in the images. However, it is optimized quite a lot. This means that only necessary files to compile plugins are kept. For example in Nuke 13 the image is only 830 mb.

Unfortunately for Windows the base image + the Visual Studio build tools is quite huge. These images are around 15gb.


## 🔨 Issues 
If you might be running into issues using these Docker images: please feel free to make an [issue](https://github.com/gillesvink/NukeVersionParser/issues) on this repository.

## Disclaimer
This project is an independent effort, not affiliated with or endorsed by Foundry. 
It provides Docker images for plugin building purposes. 
The terms "Nuke" and related trademarks are the property of Foundry, 
used here for descriptive purposes only. For official information and support, 
please refer to Foundry's [official website](https://www.foundry.com/).

By using this project, you agree on the [EULA](https://www.foundry.com/eula) provided by Foundry.