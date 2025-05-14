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
    description="Merges all audio files and a cue sheet into a m4b audiobook"
)
parser.add_argument("-i", "--inputdir", default="", help="Input directory")
parser.add_argument("-c", "--cue", default="", help="Input CUE sheet")
parser.add_argument(
    "--keep",
    default=False,
    help="Keep audio files and cue sheet after processing",
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

cmd = (
    f'ffmpeg -f concat -safe 0 -i "{input_file}" '
    f'-vn -acodec aac -ab 112000 -ar 44100 -y "{m4b_file}"',
)
sp.run(cmd, shell=True)

# Get chapters from cue sheet
cue_file = args.cue or input("Path to cue sheet: ")
with open(cue_file, "r") as f:
    cue_lines = f.readlines()

# Convert chapters into txt
chapter_file = os.path.abspath(os.path.join(folder, "chapters.txt"))
with open(chapter_file, "w") as f:
    chapter_count = 0
    prev_start = 0
    track_line = False
    title = ""
    prev_title = ""

    for line in cue_lines:
        # Check for TRACK line
        if "TRACK" in line:
            track_line = True
            continue

        # Extract title
        if "TITLE" in line and track_line:
            title = line.split('"')[1]
            track_line = False

        # Parse INDEX 01 line
        if "INDEX 01" in line and title:
            # Parse time (minutes:seconds:frames)
            _, time = line.split()
            t = time.split(":")
            start = (
                (int(t[0]) * 60 * 1000) + (int(t[1]) * 1000) + (int(t[2]) * 1000 // 75)
            )

            # If not first track, output previous chapter
            if chapter_count > 0:
                f.write("[CHAPTER]\n")
                f.write("TIMEBASE=1/1000\n")
                f.write(f"START={prev_start}\n")
                f.write(f"END={start - 1}\n")
                f.write(f"title=Chapter {chapter_count}\n\n")

                # Prepare for next iteration
                prev_start = start
                prev_title = title
                chapter_count += 1

    # # Output last chapter
    f.write("[CHAPTER]\n")
    f.write("TIMEBASE=1/1000\n")
    f.write(f"START={prev_start}\n")
    f.write("END=-1\n")
    f.write(f"title=Chapter {chapter_count}\n\n")

# Add chapters to m4b
m4b_chapterized = os.path.abspath(os.path.splitext(m4b_file)[0] + "_chapterized.m4b")
cmd = (
    f'ffmpeg -i "{m4b_file}" -f ffmetadata -i "{chapter_file}" '
    "-map 0:a -map_chapters 1 -map_metadata 1 "
    f'-acodec copy -y "{m4b_chapterized}"'
)
sp.run(cmd, shell=True)

# Cleanup
os.remove(chapter_file)

if not args.keep:
    os.remove(input_file)
    os.remove(m4b_file)
