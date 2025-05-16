cmake_minimum_required(VERSION 3.10 FATAL_ERROR)
project(NDKExamplePlugins)

set(CMAKE_MODULE_PATH "CMake;${CMAKE_MODULE_PATH}")

find_package(Nuke REQUIRED)
set(CMAKE_CXX_STANDARD 11)

function(add_example_plugin PLUGIN_NAME)
    add_nuke_plugin(${PLUGIN_NAME} ${ARGN})
    target_compile_definitions(${PLUGIN_NAME} PRIVATE FN_EXAMPLE_PLUGIN)
endfunction()


add_example_plugin(Add Add.cpp)
add_example_plugin(AddChannels AddChannels.cpp)
add_example_plugin(AddInputs AddInputs.cpp)
add_example_plugin(Assert Assert.cpp)
add_example_plugin(Blocky Blocky.cpp)
add_example_plugin(cdfReaderDeep cdfReaderDeep.cpp)
add_example_plugin(cdfWriterDeep cdfWriterDeep.cpp)
add_example_plugin(ChannelSelector ChannelSelector.cpp)
add_example_plugin(CheckerBoard2 CheckerBoard2.cpp)
add_example_plugin(ColorLookup ColorLookup.cpp)
add_example_plugin(Constant Constant.cpp)
add_example_plugin(Convolve Convolve.cpp)
add_example_plugin(CornerPin2D CornerPin2D.cpp)
add_example_plugin(crwReader crwReader.cpp)
add_example_plugin(DeepColorCorrect DeepColorCorrect.cpp)
add_example_plugin(DeepCrop DeepCrop.cpp)
add_example_plugin(DeepToImage DeepToImage.cpp)
add_example_plugin(Difference Difference.cpp)
add_example_plugin(Dilate Dilate.cpp)
add_example_plugin(DynamicKnobs DynamicKnobs.cpp)
add_example_plugin(FishEye FishEye.cpp)
add_example_plugin(GPUFileShader GPUFileShader.cpp)
add_example_plugin(Grade Grade.cpp)
add_example_plugin(IDistort IDistort.cpp)
add_example_plugin(iffReader iffReader.cpp)
add_example_plugin(Keymix Keymix.cpp)
add_example_plugin(LayerExtractor LayerExtractor.cpp)
add_example_plugin(LogGeo LogGeo.cpp)
add_example_plugin(Mirror Mirror.cpp)
add_example_plugin(my3dReader my3dReader.cpp)
add_example_plugin(my3dWriter my3dWriter.cpp)
add_example_plugin(Noise Noise.cpp)
add_example_plugin(Normalise Normalise.cpp)
add_example_plugin(NormaliseExecute NormaliseExecute.cpp)
add_example_plugin(Position Position.cpp)
add_example_plugin(Rectangle Rectangle.cpp)
add_example_plugin(Remove Remove.cpp)
add_example_plugin(Saturation Saturation.cpp)
add_example_plugin(Serialize Serialize.cpp)
add_example_plugin(SimpleBlur SimpleBlur.cpp)
add_example_plugin(Socket Socket.cpp)
add_example_plugin(Sphere Sphere.cpp)
add_example_plugin(TemporalMedian TemporalMedian.cpp)
add_example_plugin(Triangle Triangle.cpp)
add_example_plugin(UVProject UVProject.cpp)
add_example_plugin(yuvReader yuvReader.cpp)
add_example_plugin(yuvWriter yuvWriter.cpp)
add_example_plugin(Handle Handle.cpp)
add_example_plugin(Draw2D Draw2D.cpp)
add_example_plugin(Draw3D Draw3D.cpp)
add_example_plugin(SimpleAxis SimpleAxis.cpp)
if (APPLE)
    target_compile_definitions(SimpleAxis PRIVATE GL_SILENCE_DEPRECATION)
endif()
add_example_plugin(Phong Phong.cpp)


find_package(FFmpeg COMPONENTS avcodec avformat swresample swscale)
#if (FFmpeg_FOUND)
if (OFF) # FIXME: Doesn't build due to issues with the code.
    add_example_plugin(movReader
        mov/codecWhitelist.cpp
        mov/movReader.cpp
    )
    target_link_libraries(movReader PRIVATE FFmpeg::avutil FFmpeg::avcodec FFmpeg::avformat FFmpeg::swresample FFmpeg::swscale)

    add_example_plugin(movWriter
        mov/codecWhitelist.cpp
        mov/movWriter.cpp
    )
    target_link_libraries(movWriter PRIVATE FFmpeg::avutil FFmpeg::avcodec FFmpeg::avformat FFmpeg::swresample FFmpeg::swscale)
else()
    message(STATUS "FFmpeg libraries weren't found, skipping mov64Reader and mov64 Writer plugins")
endif()


find_package(OpenEXR)
if (OpenEXR_FOUND)
    add_library(ExrCommon OBJECT ExrChannelNameToNuke.cpp)
    set_target_properties(ExrCommon PROPERTIES POSITION_INDEPENDENT_CODE ON)
    target_link_libraries(ExrCommon
        PRIVATE Nuke::NDK
        PUBLIC OpenEXR::IlmImf
    )

    add_example_plugin(exrReader exrReader.cpp)
    target_link_libraries(exrReader PRIVATE ExrCommon)

    add_example_plugin(exrReaderDeep exrReaderDeep.cpp)
    target_link_libraries(exrReaderDeep PRIVATE ExrCommon)

    add_example_plugin(exrWriter exrWriter.cpp)
    target_link_libraries(exrWriter PRIVATE ExrCommon)

    add_example_plugin(exrWriterDeep exrWriterDeep.cpp)
    target_link_libraries(exrWriterDeep PRIVATE ExrCommon)
else()
    message(STATUS "OpenEXR libraries were not found, skipping exrReader/Writer plugins")
endif()


find_package(Qt5 COMPONENTS Core Gui Widgets)
if (Qt5_FOUND)
    add_example_plugin(AddCustomQt AddCustomQt.cpp)
    qt_wrap_cpp(AddCustomQt MOCSOURCES AddCustomQt.moc.h)
    target_sources(AddCustomQt PRIVATE ${MOCSOURCES})
    target_link_libraries(AddCustomQt PRIVATE Qt5::Core Qt5::Gui Qt5::Widgets)

    find_package(Murmur3 REQUIRED)
    add_example_plugin(Cryptomatte
        CryptomatteManifest.cpp
        CryptomatteMatteExpression.cpp
        CryptomatteMatteList.cpp
        CryptomattePlugin.cpp
        CryptomatteUtils.cpp)
    target_link_libraries(Cryptomatte PRIVATE Murmur3::Murmur3 Qt5::Core)
else()
    message(STATUS "Qt5 libraries were not found, skipping the Qt examples")
endif()
