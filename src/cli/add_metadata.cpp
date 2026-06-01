#include "add_metadata.h"
#include <fmt/base.h>

void AddMetadata::register_command(CLI::App &cli) {
  auto *subcommand = cli.add_subcommand("add_metadata", "Add metadata from Audible and Open Library to audiobook");

  subcommand->callback([subcommand]() {
    fmt::print("Add metadata called");
  });
}