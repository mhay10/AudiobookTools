#pragma once
#include <CLI/CLI.hpp>
#include "command.h"

class AddMetadata : public Command {
    std::string input_file;
    std::string title;
    std::vector<std::string> authors;
    std::vector<std::string> narrators;

public:
    AddMetadata() : Command(
        "add-metadata",
        "Add metadata to an audiobook from Audible and OpenLibrary"
    ) {
    }

    void add_options(CLI::App *cmd) {
        cmd->add_option("--input", input_file, "Input M4B file")->required();
        cmd->add_option("--title", title, "Title of book")->required();
        cmd->add_option("--authors", authors, "Author/s of book")->delimiter(',')->required();
        cmd->add_option("--narrators", narrators, "Narrator/s of book")->delimiter(',');
    };

    void run() override;
};
