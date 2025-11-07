# Core library
add_library(drawing_core STATIC
    # Core modules will be added here
    core/shapes/shape.cpp
    core/algorithms/bresenham.cpp
    core/rendering/engine.cpp
    core/document/manager.cpp
    core/commands/command.cpp
    core/tools/tool.cpp
    utils/logger.cpp
)

target_include_directories(drawing_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_link_libraries(drawing_core
    nlohmann_json::nlohmann_json
    Boost::boost
    # ${SKIA_LIBRARY}  # Uncomment when Skia is configured
)

# Export headers
target_include_directories(drawing_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>
)
