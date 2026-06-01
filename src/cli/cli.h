#pragma once
#include <CLI/CLI.hpp>

#include "command.h"

class Cli {
    CLI::App app{"A set of tools to help with audiobook related tasks."};
    std::vector<std::unique_ptr<Command> > commands;

public:
    void register_commands();

    int parse(int argc, char **argv);
};
