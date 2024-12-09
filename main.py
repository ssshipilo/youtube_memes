"""
This is the main loop file for our AutoTube Bot!

Quick notes!
- Currently it's set to try and post a video then sleep for a day.
- You can change the size of the video currently it's set to post shorts.
    * Do this by adding a parameter of scale to the image_save function.
    * scale=(width,height)
"""

import random
from datetime import date
import time
from utils.CreateMovie import CreateMovie, GetDaySuffix
from utils.RedditBot import RedditBot
from utils.upload_video import upload_video, send_message_to_user
import shutil
import os
from datetime import datetime, timedelta

#Create Reddit Data Bot
redditbot = RedditBot()


def generate_video():
    folder_path = os.path.join(os.getcwd(), 'video.mp4')
    if os.path.exists(folder_path):
        os.remove(folder_path)
    folder_path = os.path.join(os.getcwd(), 'video_clips.mp4')
    if os.path.exists(folder_path):
        os.remove(folder_path)
    folder_path = os.path.join(os.getcwd(), 'data')
    if os.path.exists(folder_path):
    
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        shutil.rmtree(folder_path)
    time.sleep(4)

    # Gets our new posts pass if image related subs. Default is memes
    posts = redditbot.get_posts("memes")

    # Create folder if it doesn't exist
    redditbot.create_data_folder()

    # Go through posts and find 5 that will work for us.
    for post in posts:
        result = redditbot.save_image(post)
        

    # Wanted a date in my titles so added this helper
    DAY = date.today().strftime("%d")
    DAY = str(int(DAY)) + GetDaySuffix(int(DAY))
    dt_string = date.today().strftime("%A %B") + f" {DAY}"

    # Create the movie itself!
    CreateMovie.CreateMP4(redditbot.post_data)

    # Video info for YouTube.
    # This example uses the first post title.
    video_data = {
            "file": "video.mp4",
            "title": f"{redditbot.post_data[0]['title']} - Funniest memes and comments {dt_string}!",
            "description": "#shorts\nWe give you the hottest memes of the day with funny comments!",
            "keywords":"meme,reddit,Dankestmemes,Funniest,memes",
            "privacyStatus":"public"
    }   

    
    print(f"Posting Video")
    upload_video(video_data)

    return redditbot.post_data[0]['title']


if __name__ == "__main__":
    # Leave if you want to run it 24/7
    while True:
        try:
            current_datetime = datetime.now()
            first_upload_delay_hours = random.randint(11, 13)
            first_upload_datetime = current_datetime + timedelta(hours=first_upload_delay_hours)

            second_upload_delay_hours = random.randint(11, 13)
            second_upload_datetime = first_upload_datetime + timedelta(hours=second_upload_delay_hours)

            # Ждем первой генерации
            title = generate_video()
            send_message_to_user(f"""Видео с тайтлом "{title}" загружено!!!\n\nСледующая загрузка {first_upload_datetime - current_datetime.strftime('%Y-%m-%d %H:%M:%S')}""")

            # Ждем второй генерации
            time.sleep((first_upload_datetime - current_datetime).total_seconds())
            result = generate_video()
            send_message_to_user(f"""Видео с тайтлом "{title}" загружено!!!\n\nСледующая загрузка {second_upload_datetime.strftime('%Y-%m-%d %H:%M:%S')}""")
            time.sleep((second_upload_datetime - datetime.now()).total_seconds())

        except Exception as e:
            send_message_to_user(f"На сервере ошибка {e}")
            time.sleep(60*60)
            continue