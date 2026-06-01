#include "cli.h"
#include "add_metadata.h"
#include "chapters_from_silence.h"
#include "create_from_asin.h"
#include "create_from_cue.h"
#include "create_from_files.h"

void Cli::register_commands() {
    commands.push_back(std::make_unique<AddMetadata>());
    commands.push_back(std::make_unique<ChaptersFromSilence>());
    commands.push_back(std::make_unique<CreateFromAsin>());
    commands.push_back(std::make_unique<CreateFromCue>());
    commands.push_back(std::make_unique<CreateFromFiles>());

    for (auto &command: commands) {
        command->register_command(app);
    }
    app.require_subcommand(1);
}

int Cli::parse(int argc, char **argv) {
    CLI11_PARSE(app, argc, argv);
    return 0;
}
