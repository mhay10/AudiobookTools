from urllib.request import urlopen, Request
import subprocess as sp
import argparse
import readline
import glob
import json
import os
import re


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
    description="Convert mp3 files to m4b and add chapters and cover"
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

# Converts mp3 files to m4b
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
temp_m4b_file = os.path.abspath(
    os.path.join(folder, f"{os.path.basename(folder)}_temp.m4b")
)

input_file = os.path.abspath(os.path.join(folder, "input.txt"))
with open(input_file, "w") as f:
    for mp3_file in mp3_files:
        mp3_file = mp3_file.replace("'", "'\\''")
        f.write(f"file '{os.path.abspath(mp3_file)}'\n")

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
has_intro = args.intro or (input("Has intro? (y/n): ").lower() == "y")
buffer = 0 if has_intro else 4000

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

# First command: Combine audio and chapters
cmd_audio = (
    f'ffmpeg -f concat -safe 0 -i "{input_file}" '
    f'-f ffmetadata -i "{chapters_file}" '
    f"-map 0:a -map_chapters 1 -map_metadata 1 "
    f'-metadata title="{os.path.basename(folder)}" '
    f"-c:a aac -b:a 112k -ar 44100 "
    f'-y "{temp_m4b_file}"'
)
sp.run(cmd_audio, shell=True)

# Second command: Add cover image
cmd_cover = (
    f'ffmpeg -i "{temp_m4b_file}" -i "{cover_file}" '
    "-map 0:0 -map 1:0 "
    '-id3v2_version 3 -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" '
    "-c:v libx264 "
    f'-y "{m4b_file}"'
)
sp.run(cmd_cover, shell=True)
# Cleanup

os.remove(chapters_file)
os.remove(cover_file)
os.remove(input_file)
os.remove(temp_m4b_file)

remove_mp3 = (not args.keep) or (input("Remove mp3 files? (y/n): ").lower() == "y")
if remove_mp3:
    for mp3_file in mp3_files:
        os.remove(mp3_file)
