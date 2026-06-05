cmake_minimum_required(VERSION 3.21)
project(AudiobookTools VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CPR_USE_SYSTEM_CURL OFF)
set(BUILD_SHARED_LIBS OFF)

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
        json
        GIT_REPOSITORY https://github.com/nlohmann/json.git
        GIT_TAG v3.12.0
)

fetchcontent_declare(
        fmt
        GIT_REPOSITORY https://github.com/fmtlib/fmt.git
        GIT_TAG 12.1.0
)

fetchcontent_declare(
        cpr
        GIT_REPOSITORY https://github.com/libcpr/cpr.git
        GIT_TAG 1.14.2
)

fetchcontent_makeavailable(CLI11)
fetchcontent_makeavailable(json)
fetchcontent_makeavailable(fmt)
fetchcontent_makeavailable(cpr)

# ====================
# Sources and Executable
# ====================
file(GLOB_RECURSE SOURCES src/*.cpp)
add_executable(${PROJECT_NAME} ${SOURCES}
        lib/bookinfo.h
        src/utils/open_library.cpp
        src/utils/audible.cpp
        src/utils/audible.h)

find_package(OpenSSL REQUIRED)
target_compile_definitions(${PROJECT_NAME} INTERFACE CPPHTTPLIB_OPENSSL_SUPPORT)

target_include_directories(${PROJECT_NAME} PRIVATE src)
target_include_directories(${PROJECT_NAME} PRIVATE lib)

target_link_libraries(${PROJECT_NAME} PRIVATE CLI11::CLI11)
target_link_libraries(${PROJECT_NAME} PRIVATE nlohmann_json::nlohmann_json)
target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt)
target_link_libraries(${PROJECT_NAME} PRIVATE cpr::cpr)

# ====================
# Compiler Options
# ====================
target_compile_options(${PROJECT_NAME} PRIVATE
        $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -pedantic>
        $<$<CXX_COMPILER_ID:MSVC>:/W4 /permissive->
)
