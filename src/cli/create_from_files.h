#pragma once
#include <CLI/CLI.hpp>
#include "command.h"

class CreateFromFiles : public Command {
public:
    CreateFromFiles() : Command(
        "create-from-files",
        "Create an audiobook with each file being a chapter"
    ) {
    }

    void run(CLI::App *cmd) override;
};
