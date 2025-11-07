cmake_minimum_required(VERSION 3.20)
project(NativeDrawingApp VERSION 1.0.0 LANGUAGES CXX)

# C++ 标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 选项
option(BUILD_TESTS "Build unit tests" ON)
option(ENABLE_GPU_ACCELERATION "Enable GPU acceleration" ON)
option(BUILD_NATIVE_ADDON "Build Node.js Native Addon" ON)

# 输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# 查找依赖
find_package(nlohmann_json REQUIRED)

# Skia 依赖（需要手动配置路径）
# set(SKIA_DIR "/path/to/skia" CACHE PATH "Path to Skia library")
# find_library(SKIA_LIBRARY skia PATHS ${SKIA_DIR}/out/Release)
# include_directories(${SKIA_DIR}/include)

# Boost Geometry（用于 R-tree 空间索引）
find_package(Boost REQUIRED COMPONENTS geometry)

# 测试框架
if(BUILD_TESTS)
    find_package(GTest REQUIRED)
    enable_testing()
endif()

# 平台特定设置
if(APPLE)
    set(CMAKE_MACOSX_RPATH ON)
    set(CMAKE_INSTALL_RPATH "@executable_path/../lib")
elseif(UNIX)
    set(CMAKE_INSTALL_RPATH "$ORIGIN/../lib")
endif()

# 编译选项
if(MSVC)
    add_compile_options(/W4 /WX-)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 源代码目录
add_subdirectory(src)

# 测试目录
if(BUILD_TESTS)
    add_subdirectory(tests/cpp)
endif()

# 安装规则
install(TARGETS drawing_core
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

# CPack 配置
include(CPack)
set(CPACK_PACKAGE_NAME "NativeDrawingApp")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_VENDOR "Drawing Team")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Cross-platform native drawing application")
set(CPACK_GENERATOR "DEB;RPM;NSIS;DragNDrop")
