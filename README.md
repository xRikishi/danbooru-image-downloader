# Danbooru Downloader

Danbooru Downloader is a Python script that fetches images and their associated tags from Danbooru based on user-defined search criteria. The script downloads images, skips blacklisted tags, and saves both the images and their tags to a specified folder.

## Features

- **Download Images**: Fetches images from Danbooru based on the specified tags.
- **Blacklist Tags**: Skips images that have any blacklisted tags.
- **Retries on Failure**: If the download fails, it retries up to a specified number of times.
- **Tagging**: Saves tags associated with each image into a `.txt` file.
- **Logging**: Detailed logging of the process, including successes and errors.
- **Custom Folder Structure**: Saves the images and logs in a custom folder.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python 3.x
- Required Python libraries (listed in `requirements.txt`)

To install the required libraries, run:

```bash
pip install -r requirements.txt
