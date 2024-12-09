# AutoTube Bot

AutoTube Bot is a Python script that automates the process of creating and uploading videos to YouTube. It collects information and images from Reddit posts, processes them into a video (optimized for YouTube Shorts), and uploads them to your channel with appropriate metadata.

---

## Features

- Fetches posts from Reddit (default: `r/memes`).
- Processes up to 5 Reddit posts to create a video.
- Automatically generates video titles and descriptions.
- Uploads videos to YouTube with customizable privacy settings.
- Sends notifications after video uploads.
- Designed to run continuously, posting videos at intervals.

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ssshipilo/youtube_memes.git
   cd youtube_memes
   ```

Install required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your YouTube API credentials and Reddit API credentials in `config.py` file.
    Set up Reddit API credentials:

    - Go to [Reddit API](https://www.reddit.com/prefs/apps/) and create an app
    Obtain Reddit API keys from Reddit Apps.
    Add your credentials to the RedditBot class in utils/RedditBot.py.
    Set up YouTube Data API credentials:

    - Go to [Google Cloud Console](https://console.cloud.google.com/)
    Obtain YouTube API keys from Google Cloud Console.
    Add your credentials to utils/upload_video.py.
    Usage
    Run the Bot
    Start the bot by running the main script:

```bash
python main.py
```

    The bot will:

    Fetch Reddit posts.
    Create and upload a video to YouTube.
    Wait for a random interval between 11 to 13 hours before creating the next video.

    Configuration
    Adjust Video Size
    You can change the video dimensions for YouTube Shorts or standard videos by modifying the scale parameter in the image_save function:

    ```bash
    video_data = {
        "file": "video.mp4",
        "title": "Custom Video Title",
        "description": "#shorts\nCustom description here.",
        "keywords": "meme,reddit,Dankestmemes,Funniest,memes",
        "privacyStatus": "public"
    }
    ```

## Error Handling

The bot includes basic error handling:  
- If an error occurs during video creation or upload, the bot will log the error and retry after an hour.

---

## Dependencies

The following dependencies are required to run the bot:  
- **Python 3.7+**  
- **praw** — Reddit API library.  
- **google-api-python-client** — YouTube API client.  
- **moviepy** — Video editing library.  
- **shutil** — File operations library.  
- Other utilities specified in `requirements.txt`.

---

## File Structure

- **main.py**: Entry point of the script.  
- **utils/**:  
  - `CreateMovie.py`: Handles video creation.  
  - `RedditBot.py`: Fetches Reddit posts and downloads images.  
  - `upload_video.py`: Uploads videos to YouTube and sends notifications.  
- **Data Folder**: Temporary data and files are stored in the `data/` folder. This folder is cleaned up after each run.  
- **Loop Settings**: The bot is designed to run indefinitely. To modify the loop interval, adjust the range in the main loop:  
  ```python
  random.randint(11, 13)

### Disclaimer
This script is for educational purposes. Ensure you comply with the terms and conditions of the Reddit API and YouTube Data API when using this bot.