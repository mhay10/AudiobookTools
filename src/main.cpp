#include "cli/cli.h"

int main(int argc, char **argv) {
  Cli cli;
  cli.register_commands();
  cli.parse(argc, argv);

  return 0;
}