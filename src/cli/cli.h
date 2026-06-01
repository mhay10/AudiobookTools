#pragma once
#include <CLI/CLI.hpp>

class Cli {
private:
  CLI::App app{"A set of tools to help with audiobook related tasks."};

public:
  void register_commands();
  int parse(int argc, char **argv);
};
