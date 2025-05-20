const std = @import("std");
const Builder = std.Build;
const Module = std.Build.Module;

pub fn build(b: *Builder) !void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const source_files = [_][]const u8{
        "Add.cpp",
        "AddChannels.cpp",
        "AddInputs.cpp",
        "Assert.cpp",
        "Blocky.cpp",
        "CheckerBoard2.cpp",
        "ColorLookup.cpp",
        "Constant.cpp",
        "Convolve.cpp",
        "CornerPin2D.cpp",
        "DeepColorCorrect.cpp",
        "DeepCrop.cpp",
        "DeepRead.cpp",
        "DeepToImage.cpp",
        "Dilate.cpp",
        "Draw2D.cpp",
        "Draw3D.cpp",
        "FishEye.cpp",
        "GeoTriangle.cpp",
        "GeoTwist.cpp",
        "GPUFileShader.cpp",
        "Grade.cpp",
        "Handle.cpp",
        "IDistort.cpp",
        "Keymix.cpp",
        "KnobParade.cpp",
        "LayerExtractor.cpp",
        "Mirror.cpp",
        "Noise.cpp",
        "Normalise.cpp",
        "NormaliseExecute.cpp",
        "OpenGL.cpp",
        "ParticleGravity.cpp",
        "Phong.cpp",
        "Position.cpp",
        "Remove.cpp",
        "Rectangle.cpp",
        "Saturation.cpp",
        "Serialize.cpp",
        "SimpleAxis.cpp",
        "SimpleBlur.cpp",
        "SimpleBlurCached.cpp",
        "Socket.cpp",
        "TemporalMedian.cpp",
    };

    for (source_files) |file| {
        const plugin = b.addSharedLibrary(.{
            .name = file[0 .. file.len - 4],
            .target = target,
            .optimize = optimize,
        });
        plugin.linkLibC();
        plugin.linkSystemLibrary("GL");
        plugin.linkLibCpp();
        plugin.linkSystemLibrary("DDImage");

        plugin.addSystemIncludePath(.{
            .cwd_relative = "/usr/local/nuke_install/include",
        });
        plugin.addLibraryPath(.{
            .cwd_relative = "/usr/local/nuke_install",
        });
        plugin.addSystemIncludePath(b.path("./include"));
        plugin.addLibraryPath(b.path("./"));
        plugin.addSystemIncludePath(b.path("../include"));
        plugin.addLibraryPath(b.path("../"));

        const options = Module.AddCSourceFilesOptions{
            .flags = &.{
                "-std=c++17",
                "-W",
                "-Wno-error",
                "-Wall",
                "-fPIC",
                "-Wno-unused-parameter",
            },
            .files = &.{file},
        };

        plugin.linker_allow_shlib_undefined = true;
        plugin.linker_dynamicbase = true;
        plugin.addCSourceFiles(options);
        b.installArtifact(plugin);
    }
}
