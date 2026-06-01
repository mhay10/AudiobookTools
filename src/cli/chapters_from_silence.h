#pragma once
#include <CLI/CLI.hpp>
#include "command.h"

class ChaptersFromSilence : public Command {
public:
    ChaptersFromSilence() : Command(
        "chapters-from-silence",
        "Generate chapters for an audiobook by detecting silence"
    ) {
    }

    void run() override;
};
