#pragma once
#include <CLI/CLI.hpp>
#include "command.h"

class CreateFromAsin : public Command {
public:
    CreateFromAsin() : Command(
        "create-from-asin",
        "Create an audiobook with chapter data from Audible"
    ) {
    }

    void run(CLI::App *cmd) override;
};
