#pragma once
#include <CLI/CLI.hpp>
#include "command.h"

class CreateFromCue : public Command {
public:
    CreateFromCue() : Command(
        "create-from-cue",
        "Create an audiobook with chapter data from a CUE file"
    ) {
    }

    void run(CLI::App *cmd) override;
};
