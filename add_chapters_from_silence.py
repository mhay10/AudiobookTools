import subprocess as sp
import argparse
import os


# Setup optional arguments
parser = argparse.ArgumentParser(
    description="Add chapters to an m4b audiobook from detecting silence"
)
parser.add_argument("-i", "--input", help="Input m4b file", required=True)
parser.add_argument(
    "--min",
    help="Minimum silence duration in seconds",
    type=float,
    required=True,
)
parser.add_argument(
    "--max",
    help="Maximum silence duration in seconds",
    type=float,
    required=True,
)
parser.add_argument(
    "--level",
    help="Silence level in dB (Default: -30)",
    type=float,
    default=-30,
)
parser.add_argument(
    "--overwrite",
    help="Overwrite existing chapters",
    default=False,
    action="store_true",
)

args = parser.parse_args()

# Detect silence
input_file = os.path.abspath(args.input)
min_silence = args.min
max_silence = args.max
noise_level = args.level

print(f"Detecting silence in '{os.path.basename(input_file)}'...", end=" ", flush=True)
detection_cmd = f'ffmpeg -i "{input_file}" -af silencedetect=n={noise_level}dB:d={min_silence} -f null -'
detection_output = sp.run(
    detection_cmd, shell=True, check=True, capture_output=True, text=True
).stderr
print("Done")

# Parse silence detection output
silences = []
for line in detection_output.splitlines():
    if "silence_start" in line:
        start_time = float(line.split()[-1])
    elif "silence_end" in line:
        end_time = float(line.split()[4])
        duration = float(line.split()[7])

        if duration <= max_silence + 0.25:
            print(f"Silence at: {start_time:.2f} - {end_time:.2f} ({duration:.2f}s)")
            silence = {"start": start_time, "end": end_time, "duration": duration}
            silences.append(silence)

# Create chapters file
chapters_file = os.path.abspath(
    os.path.join(os.path.dirname(input_file), "chapters.txt")
)
with open(chapters_file, "w") as f:
    current_start = 0
    for i, silence in enumerate(silences):
        title = f"Chapter {i + 1}"
        end_time = silence["end"]

        f.write(
            "[CHAPTER]\n"
            "TIMEBASE=1/1000\n"
            f"START={int(current_start * 1000)}\n"
            f"END={int(end_time * 1000)}\n"
            f"title={title}\n\n"
        )

        current_start = end_time

# Add chapters to m4b file
m4b_temp = os.path.abspath(input_file.replace(".m4b", "_temp.m4b"))
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

# Cleanup
os.remove(chapters_file)
