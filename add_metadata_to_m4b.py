from urllib.request import Request, urlopen
from urllib.parse import urlencode
import subprocess as sp
import argparse
import json
import re
import os


# Gets metadata and cover from Audible
def search_audible(title, author, narrator=None):
    # Try to find book on Audible
    params = {
        "title": title,
        "author": author,
        "product_sort_by": "Relevance",
        "num_results": 1,
    }
    if narrator:
        params["narrator"] = narrator

    url = f"https://api.audible.com/1.0/catalog/products?{urlencode(params)}"
    print(f"Audible Search URL: {url}")

    response = json.loads(get(url))
    num_results = response["total_results"]
    if num_results == 0:
        print(f"No results found for '{title}' by '{author}' on Audible\n")
        return None

    asin = response["products"][0]["asin"]
    print(f"Found ASIN for '{title}' by '{author}' on Audible: {asin}")

    # Get book cover and metadata
    url = f"https://api.audnex.us/books/{asin}"
    print(f"Audible Metadata Fetch URL: {url}")

    response = json.loads(get(url))
    metadata = {
        "title": response["title"],
        "authors": ", ".join(a["name"] for a in response["authors"]),
        "narrators": ", ".join(a["name"] for a in response["narrators"]),
        "cover": response["image"],
        "description": response["description"],
        "year": response["copyright"],
    }
    print(f"Found metadata for '{title}' by '{author}' on Audible\n")

    return metadata


# Gets metadata and cover from Google Books
def search_googlebooks(title, author):
    # Try to find book on Google Books
    params = {
        "q": f"intitle:{title}+inauthor:{author}",
        "maxResults": 1,
        "langRestrict": "en",
    }

    url = f"https://www.googleapis.com/books/v1/volumes?{urlencode(params)}"
    print(f"Google Books Search URL: {url}")

    response = json.loads(get(url))
    num_results = len(response["items"])
    if num_results == 0:
        print(f"No results found for '{title}' by '{author}' on Google Books\n")
        return None

    print(f"Found '{title}' by '{author}' on Google Books")

    # Get book cover and metadata
    url = response["items"][0]["selfLink"]
    print(f"Google Books Metadata Fetch URL: {url}")

    response = json.loads(get(url))
    vol_info = response["volumeInfo"]
    metadata = {
        "title": vol_info["title"]
        + (f" - {vol_info['subtitle']}" if "subtitle" in vol_info else ""),
        "authors": ", ".join(vol_info["authors"]),
        "narrators": "",
        "cover": vol_info["imageLinks"]["thumbnail"],
        "description": re.sub(r"<[^>]+>", "", vol_info["description"]),
        "year": vol_info["publishedDate"][:4],
    }
    print(f"Found metadata for '{title}' by '{author}' on Google Books\n")

    return metadata


# Makes web requests
def get(url: str):
    req = Request(url, headers={"User-Agent": "Totally not a bot"})
    return urlopen(req).read()


# Setup optional arguments
parser = argparse.ArgumentParser(
    description="Add metadata from OpenLibrary and Audible to an m4b file"
)
parser.add_argument("-i", "--input", default="", help="Input m4b file", required=True)
parser.add_argument(
    "-t", "--title", default="", help="Title of the audiobook", required=True
)
parser.add_argument(
    "-a",
    "--author",
    default="",
    help="Author of the audiobook (comma separated)",
    required=True,
)
parser.add_argument(
    "-n",
    "--narrator",
    default="",
    help="Narrator(s) of the audiobook (comma separated)",
)
parser.add_argument(
    "--override", default=False, help="Override existing metadata", action="store_true"
)
parser.add_argument(
    "--keep",
    default=False,
    help="Keep cover file after processing",
    action="store_true",
)

args = parser.parse_args()

# Get arguments
input_file = args.input
title = args.title
author = args.author
narrator = args.narrator or ""


# Search for metadata and combine results
audible_data = search_audible(title, author, narrator)
google_data = search_googlebooks(title, author)

metadata = {}
for key in ["title", "authors", "narrators", "cover", "description", "year"]:
    audible_value = audible_data.get(key) if audible_data else None
    google_value = google_data.get(key) if google_data else None

    if audible_value:
        metadata[key] = audible_value
    elif google_value:
        metadata[key] = google_value
    else:
        metadata[key] = None
        print(f"Could not find {key} for '{title}' by '{author}'\n")

# Download cover image
if metadata["cover"]:
    cover_url = metadata["cover"]
    print(f"Downloading cover image from {cover_url}...")

    cover_file = os.path.abspath(os.path.join(os.path.dirname(input_file), "cover.jpg"))
    with open(cover_file, "wb") as f:
        f.write(get(cover_url))

# Add metadata to m4b temp file
m4b_temp = os.path.abspath(input_file.replace(".m4b", "_temp.m4b"))
metadata_cmd = (
    f'ffmpeg -i "{input_file}" -i "{cover_file}" '
    "-map 0:a -map 1:v "
    f'-metadata title="{metadata["title"]}" '
    f'-metadata album="{metadata["title"]}" '
    f'-metadata artist="{metadata["authors"]}" '
    f'-metadata album_artist="{metadata["authors"]}" '
    f'-metadata composer="{metadata["narrators"]}" '
    f'-metadata comment="{metadata["description"]}" '
    f'-metadata date="{metadata["year"]}" '
    "-c:v png -c:a copy "
    "-disposition:v:0 attached_pic "
    "-threads 0 "
    f'-y "{m4b_temp}"'
)
sp.run(metadata_cmd, shell=True, check=True)

# Rename temp file to original if needed
if args.override:
    os.replace(m4b_temp, input_file)
    print(f"Metadata added to '{input_file}'")
else:
    os.replace(m4b_temp, input_file.replace(".m4b", "_new.m4b"))
    print(f"Metadata added to '{input_file.replace('.m4b', '_new.m4b')}'")

# Cleanup
if not args.keep and metadata["cover"]:
    os.remove(cover_file)
