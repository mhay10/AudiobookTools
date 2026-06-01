#pragma once
#include "CLI/CLI.hpp"

class Command {
public:
    Command(std::string name, std::string description)
        : name(std::move(name)), description(std::move(description)) {
    };

    void register_command(CLI::App &app) {
        auto *cmd = app.add_subcommand(name, description);
        add_options(cmd);
        cmd->callback([this, cmd]() { run(); });
    }

    virtual void run() = 0;

    virtual ~Command() = default;

protected:
    virtual void add_options(CLI::App *cmd) {
    }

private:
    std::string name;
    std::string description;
};
