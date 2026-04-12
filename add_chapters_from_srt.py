import subprocess as sp
import argparse
import re
import os

# Setup optional arguments
parser = argparse.ArgumentParser(
    description="Add chapters to an m4b audiobook from SRT file if chapters titles start with 'chapter'"
)
parser.add_argument("-i", "--input", default="", help="Input M4B file", required=True)
parser.add_argument("-s", "--srt", default="", help="Input SRT file", required=True)
parser.add_argument(
    "-k",
    "--keywords",
    default="",
    help="Keywords to search for in SRT file (comma separated)",
    required=True,
)
parser.add_argument(
    "--overwrite",
    default=False,
    help="Overwrite existing chapters",
    action="store_true",
)
parser.add_argument(
    "--keep",
    default=False,
    help="Keep SRT file after processing",
    action="store_true",
)

args = parser.parse_args()

# Search for chapters in SRT file
srt_file = os.path.abspath(args.srt)
keywords = args.keywords.split(",")
with open(srt_file, "r") as f:
    chapters = []
    chapter_num = 1
    prev_line = ""
    for i, line in enumerate(f):
        if any(
            re.search(rf"\b{keyword}\b", line, re.IGNORECASE) for keyword in keywords
        ):
            # Extract time from the previous line
            time_match = re.search(r"(\d+):(\d+):(\d+),(\d+)", prev_line)
            if time_match:
                hh, mm, ss, ms = map(int, time_match.groups())
                start_time = hh * 3600 + mm * 60 + ss + ms / 1000

                chapter = {
                    "title": f"Chapter {chapter_num}",
                    "start": start_time,
                    "line": line.strip(),
                }
                chapters.append(chapter)
                chapter_num += 1

        prev_line = line

# Create chapters file
chapters_file = os.path.abspath(os.path.join(os.path.dirname(srt_file), "chapters.txt"))
with open(chapters_file, "w") as f:
    for chapter in chapters:
        f.write(
            "[CHAPTER]\n"
            "TIMEBASE=1/1000\n"
            f"START={int(chapter['start'] * 1000)}\n"
            f"END={int((chapter['start']) * 1000)}\n"
            f"title={chapter['title']}\n\n"
        )

# Add chapters to m4b file
input_file = os.path.abspath(args.input)
m4b_temp = os.path.abspath(args.input.replace(".m4b", "_temp.m4b"))
chapters_cmd = (
    f'ffmpeg -i "{input_file}" -f ffmetadata -i "{chapters_file}" '
    "-map 0:a -map_chapters 1 -map_metadata 1 "
    "-c:a copy "
    f'-y "{m4b_temp}"'
)
sp.run(chapters_cmd, shell=True, check=True)

# Rename temp file to original if needed
if args.overwrite:
    os.replace(m4b_temp, input_file)
    print(f"Chapters added to '{input_file}'")
else:
    os.replace(m4b_temp, input_file.replace(".m4b", "_chapterized.m4b"))
    print(f"Chapters added to '{input_file.replace('.m4b', '_chapterized.m4b')}'")

# Cleanup
os.remove(chapters_file)
if not args.keep:
    os.remove(srt_file)
