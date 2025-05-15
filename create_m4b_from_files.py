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


# Get duration of audio file
def get_duration(file):
    cmd = (
        "ffprobe -v error -show_entries format=duration "
        f'-of default=noprint_wrappers=1:nokey=1 "{file}"'
    )
    result = sp.run(cmd, shell=True, capture_output=True, text=True)

    return float(result.stdout.strip())


# Setup path autocomplete
def completer(text, state):
    line = readline.get_line_buffer().split()
    return [x for x in glob.glob(text + "*")][state]


readline.set_completer_delims("\t")
readline.parse_and_bind("tab: complete")
readline.set_completer(completer)

# Setup optional arguments
parser = argparse.ArgumentParser(
    description="Creates an m4b audiobook from split audio files where each file is a chapter"
)
parser.add_argument("-i", "--inputdir", default="", help="Input directory")
parser.add_argument(
    "--keep",
    default=False,
    help="Keep audio files and cue sheet after processing",
    action="store_true",
)

args = parser.parse_args()

# Convert audio files to m4b
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

# Create chapters file
chapters_file = os.path.abspath(os.path.join(folder, "chapters.txt"))
with open(chapters_file, "w") as f:
    total_duration = 0
    for i, audio_file in enumerate(audio_files):
        title = f"Chapter {i + 1}"
        start_time = 0 if i == 0 else total_duration
        duration = get_duration(audio_file)

        f.write(
            "[CHAPTER]\n"
            "TIMEBASE=1/1000\n"
            f"START={int(start_time * 1000)}\n"
            f"END={int((start_time + duration) * 1000)}\n"
            f"title={title}\n\n"
        )

        total_duration += duration

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
