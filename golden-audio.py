from urllib.request import urlopen, Request
from urllib.parse import unquote_plus
import argparse
import readline
import glob
import re
import os


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
    description="Download audiobooks from sites like goldenaudiobooks.com, hdaudiobooks.com, etc."
)
parser.add_argument("--url", default="", help="URL to audiobook")
parser.add_argument("--output", default="", help="Output folder for mp3 files")

args = parser.parse_args()

# Create output folder
output = args.output or input("Output folder: ")
os.makedirs(output, exist_ok=True)

# Get track urls
url = args.url or input("Audiobook URL: ")
html = get(url).decode("utf-8")
tracks = re.findall(r'(?<=<a href=")https://ipaudio.*?/.*?mp3(?=">)', html)

# Download tracks
for i, track in enumerate(tracks):
    # Decode url quoting
    match = re.search(r"(?<=uploads)(/.*?/)(.*)(?=/)", track)
    filename = f"{unquote_plus(match.group(2))}_{i+1}.mp3"

    # Download file
    print(f"Now downloading file {i+1} of {len(tracks)}")
    with open(os.path.join(output, filename), "wb") as f:
        f.write(get(track))

print("Done!")
