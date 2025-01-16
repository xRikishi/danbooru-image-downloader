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
```

## How to Obtain a Danbooru API Key

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
