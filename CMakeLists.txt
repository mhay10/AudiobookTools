cmake_minimum_required(VERSION 3.21)
project(AudiobookTools VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if (WIN32)
    add_compile_definitions(_WIN32_WINNT=0x0A00)
endif ()

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
        httplib
        GIT_REPOSITORY https://github.com/yhirose/cpp-httplib
        GIT_TAG v0.46.1
)

fetchcontent_makeavailable(CLI11)
fetchcontent_makeavailable(json)
fetchcontent_makeavailable(fmt)
fetchcontent_makeavailable(httplib)

# ====================
# Sources and Executable
# ====================
file(GLOB_RECURSE SOURCES src/*.cpp)
add_executable(${PROJECT_NAME} ${SOURCES}
        lib/bookinfo.h
        src/utils/open_library.cpp)

find_package(OpenSSL REQUIRED)
target_compile_definitions(${PROJECT_NAME} PRIVATE CPPHTTPLIB_OPENSSL_SUPPORT)

target_include_directories(${PROJECT_NAME} PRIVATE src)
target_include_directories(${PROJECT_NAME} PRIVATE lib)

target_link_libraries(${PROJECT_NAME} PRIVATE CLI11::CLI11)
target_link_libraries(${PROJECT_NAME} PRIVATE nlohmann_json::nlohmann_json)
target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt)
target_link_libraries(${PROJECT_NAME} PRIVATE httplib::httplib OpenSSL::SSL OpenSSL::Crypto)

# ====================
# Compiler Options
# ====================
target_compile_options(${PROJECT_NAME} PRIVATE
                $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -pedantic>
                $<$<CXX_COMPILER_ID:MSVC>:/W4 /permissive->
)
