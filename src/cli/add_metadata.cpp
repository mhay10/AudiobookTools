#include "add_metadata.h"
#include <fmt/base.h>

#include "fmt/ranges.h"

void AddMetadata::run(CLI::App *cmd) {
    fmt::println("Input file: {}", input_file);
    fmt::println("Title: {}", title);
    fmt::println("Authors: {}", fmt::join(authors, ", "));
    fmt::println("Narrators: {}", fmt::join(narrators, ", "));
}
