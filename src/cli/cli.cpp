#include "cli.h"

void Cli::register_commands() {
  // Register your commands here
}

int Cli::parse(int argc, char **argv) {
  CLI11_PARSE(app, argc, argv);
  return 0;
}