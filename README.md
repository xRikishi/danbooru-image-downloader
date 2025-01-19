# Danbooru Downloader

Danbooru Downloader is a Python script that fetches images and their associated tags from Danbooru based on user-defined search criteria. The script downloads images, skips blacklisted tags, and saves both the images and their tags to a specified folder. Created specifically for creating datasets for LoRA training

## Features

- **Download Images**: Fetches images from Danbooru based on the specified tags.
- **Blacklist Tags**: Skips images that have any blacklisted tags.
- **Retries on Failure**: If the download fails, it retries up to a specified number of times.
- **Tagging**: Saves tags associated with each image into a `.txt` file.
- **Logging**: Detailed logging of the process, including successes and errors.
- **Custom Folder Structure**: Saves the images and logs in a custom folder.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python 3.7 or higher
- Dependencies: Install via `pip install -r requirements.txt`


### Required Python Libraries
- `requests`
- `Pillow`
- `logging`



## Installation
1. Clone the repository or download the script:
   ```bash
   git clone https://github.com/xRikishi/danbooru-image-downloader.git
   cd danbooru-image-downloader
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Step 1: Set Up Your Danbooru Account

To use this script, you need a Danbooru account and an API key. Follow these steps to obtain it:

1. **Create an Account**  
   Visit [Danbooru](https://danbooru.donmai.us/) and register for an account if you don’t already have one.

2. **Access Your API Key**  
   - Log in to your Danbooru account.  
   - Navigate to your account settings by clicking on ***My Account*** in the top-left corner. Scroll down the page, and then click on ***View*** near the "API Key" label.
   - Click on the blue ***+ Add*** button.
   - It is enough to fill ***Name*** and press ***Create***. You can write anything here, it won't be needed in the script. You don't have to set ***Permissions***.
   - Copy the provided API key.  

3. **Set the API Key in the Script**  
   Open the script and update the following lines with your Danbooru username and API key:  
   ```python
   USERNAME = "your_danbooru_name"
   API_KEY = "your_danbooru_account_api"

---

### Step 2: Configure the Script
Edit the following variables in the script to suit your preferences:
- `USERNAME`: Your Danbooru username.
- `API_KEY`: Your Danbooru API key.
- `TAGS`: Tags to filter images. (e.g., `genshin_impact ocean`).
- `MIN_IMAGE_WIDTH` and `MIN_IMAGE_HEIGHT`: Minimum dimensions for images to download.
- `MAX_IMAGE_WIDTH` and `MAX_IMAGE_HEIGHT`: Maximum dimensions for images to download.
- `BLACKLIST_TAGS`: A set of tags to exclude.

---

### Step 3: Run the Script
Execute the script with:
```bash
python danbooru.py
```

---

## Resuming Downloads
The script supports resuming downloads by setting `START_PAGE`. 
- To resume from a specific page, update the `START_PAGE` variable in the script.

---

## Output Structure
- **Images**: Saved in the `danbooru_downloads` folder.
- **Tags**: Saved as `.txt` files alongside the images.
- **Logs**: Stored in `danbooru_downloads/log`.

---

## Example
```python
# Example Configuration
USERNAME = "example_username"
API_KEY = "example_api_key"
TAGS = "hatsune_miku rating:general"
MIN_IMAGE_WIDTH = 480
MIN_IMAGE_HEIGHT = 480
```



