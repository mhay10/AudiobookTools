from urllib.request import urlopen, Request
import subprocess as sp
import argparse
import readline
import glob
import json
import os
import re


# Natural sort function
def natural_sort(lst):
    def sort_key(key):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", key)]

    return sorted(lst, key=sort_key)


# Makes web requests
def get(url: str):
    req = Request(url, headers={"User-Agent": "Totally not a bot"})
    return urlopen(req).read()


# Setup path autocomplete
def completer(text, state):
    line = readline.get_line_buffer().split()
    return [x for x in glob.glob(text + "*")][state]


readline.set_completer_delims("\t")
readline.parse_and_bind("tab: complete")
readline.set_completer(completer)

# Setup optional arguments
parser = argparse.ArgumentParser(
    description="Convert audio files to m4b and add chapters and cover using Audible API"
)
parser.add_argument("-i", "--inputdir", default="", help="Input directory")
parser.add_argument("--asin", default="", help="Audible book id")
parser.add_argument(
    "--intro",
    default=False,
    help="Does book have 'This is Audible' at start?",
    action="store_true",
)
parser.add_argument(
    "--keep", default=False, help="Keep mp3 files after processing", action="store_true"
)

args = parser.parse_args()

# Converts audio files to m4b
glob_path = args.inputdir or input("Path to audio files: ")

audio_files = glob.glob(f"{glob_path}/*.mp3")
audio_files += glob.glob(f"{glob_path}/*.m4b")
audio_files += glob.glob(f"{glob_path}/*.aac")
audio_files += glob.glob(f"{glob_path}/*.m4a")
audio_files += glob.glob(f"{glob_path}/*.wav")

audio_files = natural_sort(audio_files)

folder = os.path.dirname(audio_files[0]) or "./"
m4b_file = os.path.abspath(os.path.join(folder, f"{os.path.basename(folder)}.m4b"))
temp_m4b_file = os.path.abspath(
    os.path.join(folder, f"{os.path.basename(folder)}_temp.m4b")
)

input_file = os.path.abspath(os.path.join(folder, "input.txt"))
with open(input_file, "w") as f:
    for audio_file in audio_files:
        audio_file = audio_file.replace("'", "'\\''")
        f.write(f"file '{os.path.abspath(audio_file)}'\n")

# Get chapters from Audible API
asin = args.asin or input("Audible ID: ")

url = f"https://api.audnex.us/books/{asin}/chapters"
res = get(url).decode("utf-8")
chapters = json.loads(res)["chapters"]

# Get book cover from Audible API
url = f"https://api.audnex.us/books/{asin}"
res = get(url).decode("utf-8")
cover_url = json.loads(res)["image"]

cover_file = os.path.join(folder, "cover.jpg")
with open(cover_file, "wb") as f:
    f.write(get(cover_url))

# Add chapter buffer if intro not present
buffer = 0 if args.intro else 4000

# Convert chapters into metadata format
chapters_file = os.path.join(folder, "chapters.txt")
with open(chapters_file, "w") as f:
    for i, chapter in enumerate(chapters):
        title = chapter["title"]
        start = chapter["startOffsetMs"] - buffer
        end = start + chapter["lengthMs"]

        f.write(
            "[CHAPTER]\n"
            "TIMEBASE=1/1000\n"
            f"START={start}\n"
            f"END={end}\n"
            f"title={title}\n\n"
        )

# Combine audio, metadata, and cover into M4B file
cmd_combined = (
    f'ffmpeg -f concat -safe 0 -i "{input_file}" '  # Concatenate audio files
    f'-f ffmetadata -i "{chapters_file}" '  # Metadata file for chapters
    f'-i "{cover_file}" '  # Cover image
    f"-map 0:a -map_chapters 1 -map_metadata 1 "  # Use audio stream, chapters, and metadata
    f"-map 2:v "  # Use the cover image as video stream
    f'-metadata title="{os.path.basename(folder)}" '  # Set metadata title
    f"-c:a aac -b:a 112k -ar 44100 "  # Audio encoding settings
    "-c:v libx264 "  # Encode cover image as video
    '-id3v2_version 3 -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" '  # Cover metadata
    f'-y "{m4b_file}"'  # Output file
)
sp.run(cmd_combined, shell=True)

# Cleanup
os.remove(chapters_file)
os.remove(cover_file)
os.remove(input_file)

if not args.keep:
    for audio_file in audio_files:
        os.remove(audio_file)
