import subprocess as sp
import argparse
import readline
import glob
import os
import re


# Natural sort function
def natural_sort(lst):
    def sort_key(key):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", key)]

    return sorted(lst, key=sort_key)


# Setup path autocomplete
def completer(text, state):
    line = readline.get_line_buffer().split()
    return [x for x in glob.glob(text + "*")][state]


readline.set_completer_delims("\t")
readline.parse_and_bind("tab: complete")
readline.set_completer(completer)

# Setup optional arguments
parser = argparse.ArgumentParser(
    description="Merges all audio files and a cue file into a m4b audiobook"
)
parser.add_argument("-i", "--inputdir", default="", help="Input directory")
parser.add_argument("-c", "--cue", default="", help="Input CUE file")
parser.add_argument(
    "--keep",
    default=False,
    help="Keep audio files and cue file after processing",
    action="store_true",
)

args = parser.parse_args()

# Convert mp3 files to m4b
glob_path = args.inputdir or input("Path to audio files: ")

audio_files = glob.glob(f"{glob_path}/*.mp3")
audio_files += glob.glob(f"{glob_path}/*.m4b")
audio_files += glob.glob(f"{glob_path}/*.aac")
audio_files += glob.glob(f"{glob_path}/*.m4a")
audio_files += glob.glob(f"{glob_path}/*.wav")

audio_files = natural_sort(audio_files)

folder = os.path.dirname(audio_files[0]) or "./"
m4b_file = os.path.abspath(os.path.join(folder, f"{os.path.basename(folder)}.m4b"))

input_file = os.path.abspath(os.path.join(folder, "input.txt"))
with open(input_file, "w") as f:
    for audio_file in audio_files:
        audio_file = audio_file.replace("'", "'\\''")
        f.write(f"file '{os.path.abspath(audio_file)}'\n")

# Get chapters from CUE file
cue_file = os.path.abspath(args.cue or input("Path to CUE file: "))
with open(cue_file, "r") as f:
    chapters = []
    tracks = re.split(r"(?=TRACK)", f.read())
    for track in tracks:
        if "TRACK" in track:
            lines = track.splitlines()
            chapter = {}
            for line in lines:
                if "TRACK" in line:
                    chapter["track"] = line.split()[1]
                if "TITLE" in line:
                    chapter["title"] = line.split('"')[1]
                if "INDEX 01" in line:
                    mm, ss, ff = map(int, line.split()[2].split(":"))
                    chapter["start"] = mm * 60 + ss + ff / 75

            chapters.append(chapter)

# Create chapters file
chapters_file = os.path.abspath(os.path.join(folder, "chapters.txt"))
with open(chapters_file, "w") as f:
    for i, chapter in enumerate(chapters):
        title = chapter["title"]
        start_time = chapter["start"]

        f.write(
            "[CHAPTER]\n"
            "TIMEBASE=1/1000\n"
            f"START={int(start_time * 1000)}\n"
            f"END={int(start_time * 1000)}\n"
            f"title={title}\n\n"
        )

# Combine audio and chapters into M4B file
cmd = (
    f'ffmpeg -f concat -safe 0 -i "{input_file}" '
    f'-f ffmetadata -i "{chapters_file}" '
    "-map 0:a -map_chapters 1 -map_metadata 1 "
    f'-metadata title="{os.path.basename(folder)}" '
    "-c:a aac -b:a 112k -ar 44100 "
    f'-y "{m4b_file}"'
)
sp.run(cmd, shell=True)

# Cleanup
os.remove(chapters_file)
os.remove(input_file)

if not args.keep:
    for audio_file in audio_files:
        os.remove(audio_file)
    os.remove(cue_file)
