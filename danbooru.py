import requests
import os
import time
import re
from PIL import Image
from io import BytesIO
from http.client import IncompleteRead
import logging
from collections import defaultdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from os import cpu_count

API_URL = "https://danbooru.donmai.us/posts.json"


# Your Danbooru data
USERNAME = "your_danbooru_name"  # Your Danbooru username
API_KEY = "your_danbooru_account_api"  # Your Danbooru API key



# Your download settings
SAVE_FOLDER = "danbooru_downloads"  # Folder where images and tags will be saved
TAGS = "tag1 tag2"  # Tags to filter images (space-separated). Max 2 tags for free users
# Example 1. TAGS = "genshin_impact ocean" 
# Example 2. TAGS = "hatsune_miku rating:general" 
# Example 3. TAGS = "id:5000000..9000000 2b_(nier:automata)" 
# Example 4. TAGS = "score:200 2girls" 

TAGS_TO_TRIGGER_WORDS = True # If True, tags from TAGS will be added to the beginning of the file
ADD_OWN_TRIGGER_WORDS = "" # Empty to add nothing. 
#Usage example ADD_OWN_TRIGGER_WORDS = "I love Miku"


LIMIT_PER_PAGE = 200  # Number of posts to fetch per page (max 200)
MAX_PAGES = None  # Max number of pages to fetch (None for no limit)
START_PAGE = 0  # Start from this page (for resuming downloads)
END_PAGE = float('inf') # End at this page. float('inf') is for all pages

# Tags that will be skipped if present in the post
BLACKLIST_TAGS = { # Example of excluding tags related to text
    
    # Tags related to text and metadata
    "translated", "translation_request",
    "lowres", "traditional_media", "animated", 
    "check_translation", "animated_gif", "watermark", "copyright_notice", "artist_name", "signature", 
    "twitter_username", "web_address",

    # Tags related to translations
    "alternate_language", "check_translation", "hard-translated", "partially_translated", 
    "poorly_translated", "reverse_translation", "translated", "translation_request", 

    # Tags related to image metadata
    "artist_name", "character_name", "circle_name", "commissioner_name", "company_name", "completion_time", 
    "copyright_name", "dated", "group_name", "logo", "content_rating", "twitter_username", "signature", 
    "character_signature", "song_name", "watermark", "web_address", "weapon_name",
}  

MAX_RETRIES = 5  # Maximum number of retries for downloading an image

MIN_IMAGE_WIDTH = 480
MIN_IMAGE_HEIGHT = 480
MAX_IMAGE_WIDTH = 32000
MAX_IMAGE_HEIGHT = 32000

MIN_DATE = "1990-01-01"  # YYYY-MM-DD 
MAX_DATE = "2035-12-31"  # YYYY-MM-DD

MIN_SCORE = None
MAX_SCORE = None

MIN_ID = None
MAX_ID = None

ALLOWED_RATINGS = {"e","g","q","s"} # e - explicit, g - general, q - questionable, s - sensitive 



# Logging settings
LOG_FOLDER = os.path.join(SAVE_FOLDER, "log")  # Folder for logs
LOG_FILE = os.path.join(LOG_FOLDER, "log.txt")  # File for logging download activities

# Create folders for saving images and logs if they don't exist
os.makedirs(SAVE_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# Configure logging to output messages to both a log file and the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def is_blacklisted(tags):
    """
    Check if any tag in the blacklist is present in the post's tags.
    :param tags: String of tags from the post.
    :return: True if any blacklisted tag is found, False otherwise.
    """
    return any(tag in BLACKLIST_TAGS for tag in tags.split())

def download_image_with_retries(image_url, retries=MAX_RETRIES):
    """
    Download an image with retries in case of failure.
    :param image_url: URL of the image to download.
    :param retries: Number of retry attempts.
    :return: Image data if download is successful.
    :raises: Exception if all retry attempts fail.
    """
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(image_url, timeout=10)  # Request the image with a timeout
            response.raise_for_status()  # Raise an error for HTTP codes >= 400
            return response.content  # Return the raw image data
        except (requests.RequestException, IncompleteRead) as e:
            attempt += 1
            logging.warning(f"Retry {attempt}/{retries} for {image_url}: {e}")
            time.sleep(2)  # Wait before retrying
    raise Exception(f"❌Failed to download image after {retries} attempts: {image_url}")


def download_images():
    """
    Main function to fetch and download images and tags from Danbooru.
    """
    page = START_PAGE
    downloaded_formats = defaultdict(int)  # Dictionary to track the number of files downloaded per format
    max_workers = max(1, cpu_count() - 1)
    with ThreadPoolExecutor(max_workers) as executor:
        futures = []  # List to store future tasks

        while (page < END_PAGE):
            logging.info(f"Fetching page {page}...")  # Log the current page being fetched
            params = {
                "tags": TAGS,
                "limit": LIMIT_PER_PAGE,
                "page": page,
                "login": USERNAME,
                "api_key": API_KEY,
            }
            response = requests.get(API_URL, params=params)  # Fetch posts from Danbooru API

            if response.status_code == 200:  # Check if the request was successful
                posts = response.json()
                if not posts:  # Stop if there are no more posts
                    logging.info("✅ No more posts to download.")
                    break

                for post in posts:
                    image_url = post.get("file_url")  # Get the URL of the image
                    if not image_url:
                        continue
                    
                    # Skip posts with blacklisted tags
                    blacklisted_tags = [tag for tag in post.get("tag_string", "").split() if tag in BLACKLIST_TAGS]

                    if blacklisted_tags:
                        logging.info(f"⏩ Skipped blacklisted post ID {post['id']}. Blacklisted tags: {', '.join(blacklisted_tags)}")
                        continue

                    # Skip too small or too big
                    if post["image_width"] < MIN_IMAGE_WIDTH or post["image_height"] < MIN_IMAGE_HEIGHT or post["image_width"] >= MAX_IMAGE_WIDTH or post["image_height"] >= MAX_IMAGE_HEIGHT:
                        info_image_width = post["image_width"]
                        info_image_height = post["image_height"]
                        logging.info(f"⏩ Skipped small/large size post ID {post['id']} ({info_image_width}x{info_image_height})")
                        continue

                    # Filter by ID
                    if MIN_ID is not None and post["id"] < MIN_ID:
                        logging.info(f"⏩ Min ID is {MIN_ID}. Skipped post ID {post['id']}")
                        continue
                    if MAX_ID is not None and post["id"] > MAX_ID:
                        logging.info(f"⏩ Max ID is {MAX_ID}. Skipped post ID {post['id']}")
                        continue

                    # Filter by creation date
                    post_date = datetime.fromisoformat(post["created_at"]).replace(tzinfo=None)
                    if MIN_DATE and post_date < datetime.fromisoformat(MIN_DATE):
                        logging.info(f"⏩ Min date is {MIN_DATE}. Post date is {post_date}. Skipped post ID {post['id']}")
                        continue
                    if MAX_DATE and post_date > datetime.fromisoformat(MAX_DATE):
                        logging.info(f"⏩ Max date is {MAX_DATE}. Post date is {post_date}. Skipped post ID {post['id']}")
                        continue

                    # Filter by score
                    if MIN_SCORE is not None and post["score"] < MIN_SCORE:
                        logging.info("⏩ Min score is {}. Post score is {}. Skipped post ID {}".format(MIN_SCORE, post["score"], post["id"]))
                        continue
                    if MAX_SCORE is not None and post["score"] > MAX_SCORE:
                        logging.info("⏩ Max score is {}. Post score is {}. Skipped post ID {}".format(MAX_SCORE, post["score"], post["id"]))
                        continue

                    # Filter by rating
                    if ALLOWED_RATINGS and post["rating"] not in ALLOWED_RATINGS:
                        logging.info("⏩ Post has rating \"{}\". Skipped post ID {}".format(post["rating"], post["id"]))
                        continue
                    
                    try:
                        # Save content with ID and tags in file name
                        tags_file_name = []
                        #tags_file_name.extend(post.get("tag_string_artist", "").split())
                        tags_file_name.extend(post.get("tag_string_character", "").split())
                        tags_file_name.extend(post.get("tag_string_copyright", "").split())
                        tags_file_name.extend(post.get("tag_string_general", "").split())
                        #tags_file_name.extend(post.get("tag_string_meta", "").split())

                        tags_file_name = tags_file_name[:50] # Max 50 first tags
                        invalid_chars = r'[\/:*?"<>|]'
                        tags_file_name = [re.sub(invalid_chars, "_", tag) for tag in tags_file_name]
                        tags_str = "_".join(tags_file_name)
                        if len(tags_str) > 210:
                            tags_str = tags_str[:210]

                        filename = f"{post['id']}_"

                        for tag in tags_file_name:
                            if len(filename) + len(tag) + 1 > 220:
                                break
                            filename += tag + "_"

                        filename = filename.replace("\\\\", "").replace("/", "").replace("\\", "")

                        filename = filename.rstrip("_")[:220]
                        filename_base = os.path.join(SAVE_FOLDER, filename)

                        # Check if the image file has already been downloaded
                        existing_file = next((f for f in os.listdir(SAVE_FOLDER) if f.startswith(f"{post['id']}") and not f.endswith(".txt")), None)
                        if existing_file:
                            logging.info(f"⏩ Skipped already downloaded file ID {post['id']} ({existing_file})")
                            continue
                        
                        # Submit the image download task to the executor
                        futures.append(executor.submit(download_and_save_image, post, filename_base, image_url, downloaded_formats))

                    
                    except Exception as e:
                        logging.error(f"⚠️ Error processing post ID {post['id']}: {e}")  # Log any errors during processing

                page += 1  # Move to the next page
                if MAX_PAGES and page > MAX_PAGES:  # Stop if the max page limit is reached
                    logging.info(f"✅ Reached the limit of {MAX_PAGES} pages.")
                    break

                time.sleep(1)  # Pause to respect API rate limits
            else:
                logging.error(f"⚠️ Error: {response.status_code} - {response.text}")  # Log any API errors
                break

        # Wait for all threads to finish
        for future in as_completed(futures):
            future.result()  # Ensure all tasks complete and handle any exceptions

    # Log a summary of the downloaded file formats
    logging.info("Download summary:")
    for ext, count in downloaded_formats.items():
        logging.info(f"Format {ext}: {count} files downloaded.")


def download_and_save_image(post, filename_base, image_url, downloaded_formats):
    try:
        # Download the image data
        image_data = download_image_with_retries(image_url)
        # Defining the file extension from the URL
        file_ext = os.path.splitext(image_url)[1].lower().strip(".")  # for example, 'jpg', 'mp4', 'gif'

        # If it's a video or a (mp4, webm and other), just save it without opening the PIL
        if file_ext in {"mp4", "webm", "swf", "zip", "avif"}:
            video_filename = f"{filename_base}.{file_ext}"
            with open(video_filename, "wb") as f:
                f.write(image_data)
            logging.info(f"🎥 Video downloaded: {video_filename}")
            downloaded_formats[file_ext] += 1
        else:
            # Open the image via PIL only if it is not a video
            image = Image.open(BytesIO(image_data))
            # Saving the image
            extension = image.format.lower()
            image_filename = f"{filename_base}.{extension}"
            with open(image_filename, "wb") as f:
                f.write(image_data)
            logging.info(f"🖼️ Image downloaded: {image_filename}")
            downloaded_formats[extension] += 1

        # Save the tags associated with the image
        tag_types = {
            #"artist": post.get("tag_string_artist", "").split(),
            "copyright": post.get("tag_string_copyright", "").split(),
            "character": post.get("tag_string_character", "").split(),
            "general": post.get("tag_string_general", "").split(),
            #"meta": post.get("tag_string_meta", "").split(),
        }
        filtered_tags = sum(tag_types.values(), [])  # Combine tags from all categories

        # Join tags with a comma and a space first
        tags_string = ", ".join(filtered_tags)  # Join tags with a comma and a space
        # Then replace underscores with spaces
        formatted_tags_string = tags_string.replace("_", " ")

        # Save to file
        tags_file = f"{filename_base}.txt"  # Create the filename for the tags
        with open(tags_file, "w", encoding="utf-8") as file:
            file.write(formatted_tags_string)  # Write the formatted tags to the file

        logging.info(f"Tags saved: {tags_file}")  # Log the successful save of tags

    except Exception as e:
        logging.error(f"⚠️ Error processing post ID {post['id']}: {e}")  # Log any errors during processing


def search_tags_to_triggers():
    if not TAGS_TO_TRIGGER_WORDS:
        return
    
    tags_to_prioritize = {tag.replace('_', ' ') for tag in TAGS.split()}
    logging.info(f"📄 Start of replacing search tags to triggers...")
    for filename in os.listdir(SAVE_FOLDER):
        if filename.endswith(".txt"):
            filepath = os.path.join(SAVE_FOLDER, filename)
            
            with open(filepath, "r", encoding="utf-8") as file:
                tags = file.read().strip().split(", ")
            
            prioritized_tags = [tag for tag in tags_to_prioritize if tag in tags]
            other_tags = [tag for tag in tags if tag not in tags_to_prioritize]
            
            sorted_tags = prioritized_tags + other_tags
            
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(", ".join(sorted_tags))
    logging.info(f"📄 End of replacing search tags to triggers.")
    

def add_own_triggers():
    
    if ADD_OWN_TRIGGER_WORDS.strip() != "":
        logging.info(f"📄 Start of own trigger word adding...")
        for filename in os.listdir(SAVE_FOLDER):
            if filename.endswith(".txt"):
                filepath = os.path.join(SAVE_FOLDER, filename)
                
                # Open the file for reading
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read().strip()

                # Open the file for recording and add own trigger word to the beginning
                with open(filepath, "w", encoding="utf-8") as file:
                    content = ADD_OWN_TRIGGER_WORDS + ", " + content
                    content = content.replace(", ,", ",")
                    content = content.replace(",,", ",")
                    content = content.replace("  ", " ")
                    content = content.replace("  ", " ")
                    
                    file.write(content)  # Adding own trigger word before the content
                    
        logging.info(f"📄 End of own trigger word processing.")

    


if __name__ == "__main__":
    download_images()
    search_tags_to_triggers()
    add_own_triggers()  