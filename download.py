from pydeezer.constants import track_formats
from pydeezer import Deezer, Downloader
import argparse
import readline
import glob
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
    description="Download albums and playlists from Deezer"
)
parser.add_argument("--arl", default="", help="Auth token for deezer account")
parser.add_argument("--url", default="", help="URL to deezer album/playlist")
parser.add_argument("--downdir", default="", help="Download folder for mp3 files")

args = parser.parse_args()

# Login to Deezer
arl = args.arl or input("Deezer ARL: ")
dz = Deezer(arl=arl)
user = dz.user
print("Logged in as", user["name"])

# Get playlist/album tracks
url = args.url or input("Playlist/Album URL: ")

url_id = url.split("/")[-1]
if "playlist" in url:
    tracks = dz.get_playlist_tracks(url_id)
elif "album" in url:
    tracks = dz.get_album_tracks(url_id)

print("Got tracks from", tracks[0]["ART_NAME"], "-", tracks[0]["ALB_TITLE"])

# Download tracks
track_ids = [track["SNG_ID"] for track in tracks]

download_dir = args.downdir or input("Download directory: ")
output_folder = os.path.join(
    download_dir, f'{tracks[0]["ART_NAME"]} - {tracks[0]["ALB_TITLE"]}'
)

downloader = Downloader(
    dz,
    track_ids,
    os.path.abspath(output_folder),
    quality=track_formats.MP3_128,
    concurrent_downloads=4,
)

downloader.start()
