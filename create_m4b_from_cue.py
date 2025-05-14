import subprocess as sp
import argparse
import readline
import glob
import os
import re


# Setup path autocomplete
def completer(text, state):
    line = readline.get_line_buffer().split()
    return [x for x in glob.glob(text + "*")][state]


readline.set_completer_delims("\t")
readline.parse_and_bind("tab: complete")
readline.set_completer(completer)

# Setup optional arguments
parser = argparse.ArgumentParser(
    description="Merges all mp3 files and a cue sheet into a m4b audiobook"
)
parser.add_argument("-i", "--inputdir", default="", help="Input directory")
parser.add_argument("-c", "--cue", default="", help="Cue sheet")
parser.add_argument(
    "--keep",
    default=False,
    help="Keep audio files and cue sheet after processing",
    action="store_true",
)

args = parser.parse_args()

# Convert mp3 files to m4b
glob_path = args.inputdir or input("Path to audio files: ")

mp3_files = glob.glob(f"{glob_path}/*.mp3")
mp3_files += glob.glob(f"{glob_path}/*.m4b")
mp3_files += glob.glob(f"{glob_path}/*.aac")
mp3_files += glob.glob(f"{glob_path}/*.m4a")
mp3_files += glob.glob(f"{glob_path}/*.wav")
if len(mp3_files) > 1:
    mp3_files.sort(key=lambda f: int(re.findall(r"\d+", os.path.basename(f))[-2]))

folder = os.path.dirname(mp3_files[0]) or "./"
m4b_file = os.path.abspath(os.path.join(folder, f"{os.path.basename(folder)}.m4b"))

input_file = os.path.abspath(os.path.join(folder, "input.txt"))
with open(input_file, "w") as f:
    for mp3_file in mp3_files:
        mp3_file = mp3_file.replace("'", "'\\''")
        f.write(f"file '{os.path.abspath(mp3_file)}'\n")

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
                f.write(f"END={start - 1}\n\n")

                # Prepare for next iteration
                prev_start = start
                prev_title = title
                chapter_count += 1

    # # Output last chapter
    # f.write("[CHAPTER]\n")
    # f.write("TIMEBASE=1/1000\n")
    # f.write(f"START={prev_start}\n")
    # f.write("END=-1\n")
    # f.write(f"title={prev_title}\n")

# Add chapters to m4b
m4b_chapterized = os.path.abspath(os.path.splitext(m4b_file)[0] + "_chapterized.m4b")
cmd = (
    f'ffmpeg -i "{m4b_file}" -f ffmetadata -i "{chapter_file}" '
    "-map 0:a -map_chapters 1 -map_metadata 1 "
    f'-acodec copy -y "{m4b_chapterized}"'
)
sp.run(cmd, shell=True)
