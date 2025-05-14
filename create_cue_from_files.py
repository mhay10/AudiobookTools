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
    description="Creates a cue sheet using each audio file as a chapter"
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
cue_file = os.path.abspath(os.path.join(folder, f"{os.path.basename(folder)}.cue"))

# Convert audio files to cue sheet
with open(cue_file, "w") as f:
    f.write(f'TITLE "{os.path.basename(folder)}"\n\n')

    total_duration = 0
    for i, audio_file in enumerate(audio_files):
        # Get file info
        filename = os.path.basename(audio_file)
        duration = get_duration(audio_file)
        start_time = f"{int(total_duration // 3600):02d}:{int((total_duration % 3600) // 60):02d}:{int(total_duration % 60):02d}"
        print(
            f"Chapter {i+1}: {filename} - Duration: {duration:.2f}s - Start Time: {start_time}"
        )

        # Write chapter info to cue sheet
        f.write(f"TRACK {i+1} AUDIO\n")
        f.write(f'  TITLE "Chapter {i+1}"\n')
        f.write(f"  INDEX 01 {start_time}\n\n")

        # Update total duration
        total_duration += duration
