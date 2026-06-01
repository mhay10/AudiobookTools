cmake_minimum_required(VERSION 3.21)
project(AudiobookTools VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ====================
# Dependencies
# ====================
include(FetchContent)

fetchcontent_declare(
        CLI11
        GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
        GIT_TAG v2.6.2
)

fetchcontent_declare(
        fmt
        GIT_REPOSITORY https://github.com/fmtlib/fmt.git
        GIT_TAG 12.1.0
)

fetchcontent_makeavailable(CLI11)
fetchcontent_makeavailable(fmt)

# ====================
# Source Files
# ====================
file(GLOB_RECURSE SOURCES src/*.cpp)
add_executable(${PROJECT_NAME} ${SOURCES})

target_include_directories(${PROJECT_NAME} PRIVATE src)

target_link_libraries(${PROJECT_NAME} PRIVATE CLI11::CLI11)
target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt)

# ====================
# Compiler Options
# ====================

target_compile_options(${PROJECT_NAME} PRIVATE
        $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -pedantic>
        $<$<CXX_COMPILER_ID:MSVC>:/W4 /permissive->
)
