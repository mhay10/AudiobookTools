from urllib.parse import unquote
import requests
import argparse
import readline
import glob
import re
import os

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
res = requests.get(url)
audio_urls = re.findall(r'(?<=<a href=")https:\/\/ipaudio\.club\/.*?(?=">)', res.text)

# Download tracks
for i, url in enumerate(audio_urls):
    # Decode url quotes for filename
    match = re.search(r"(?<=uploads)(\/.*?\/)(.*)(?=\/)", url)
    filename = f"{unquote(match.group(2))}_{i+1}.mp3"

    # Download file
    print(f"Now downloading file {i+1} of {len(audio_urls)}")
    with open(os.path.join(output, filename), "wb") as f:
        f.write(requests.get(url).content)

print("Done!")
