from moviepy.editor import *
import random
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import textwrap

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def GetDaySuffix(day):
    if day == 1 or day == 21 or day == 31:
        return "st"
    elif day == 2 or day == 22:
        return "nd"
    elif day == 3 or day == 23:
        return "rd"
    else:
        return "th"

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
music_path = os.path.join(dir_path, "Music/")

def add_return_comment(comment):
    need_return = 30
    new_comment = ""
    return_added = 0
    return_added += comment.count('\n')
    for i, letter in enumerate(comment):
        if i > need_return and letter == " ":
            letter = "\n"
            need_return += 30
            return_added += 1
        new_comment += letter
    return new_comment, return_added

def create_text_image(text, font_path, font_size, max_width=1080*0.6, padding=10, border=3, balloon_color="white", text_color="black", avatar_size=70):
    font = ImageFont.truetype(font_path, font_size)

    # Создаем изображение для измерения размера текста
    dummy_img = Image.new("RGBA", (int(max_width), 1000), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy_img)
    # Разбиение текста на строки с учетом максимальной ширины
    lines = []
    line = ""
    for word in text.split():
        if draw.textsize(line + word, font=font)[0] <= max_width - 2 * padding - 2 * border:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    # Рассчитываем размеры изображения
    text_width, text_height = draw.multiline_textsize("\n".join(lines), font=font)
    img_width, img_height = text_width + 2 * padding + 2 * border, text_height + 2 * padding + 2 * border

    # Создаем финальное изображение
    img = Image.new("RGBA", (img_width, img_height + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Закругленный ректангл
    radius = 10
    draw.rounded_rectangle([(border, border), (img_width - border, img_height - border)], fill=balloon_color, outline=text_color, width=border, radius=radius)

    # Треугольник
    triangle = [(border + 5, img_height - border), (border + 25, img_height - border), (border + 15, img_height + 10)]
    draw.polygon(triangle, fill=balloon_color, outline=text_color)

    # Текст
    draw.multiline_text((padding + border, padding + border), "\n".join(lines), fill=text_color, font=font)

    # Сохраняем изображение
    text_image_path = os.path.join(os.getcwd(), "text_with_triangle.png")
    img.save(text_image_path, "PNG")

    # Загружаем сохраненное изображение и увеличиваем его слева на 60 пикселей
    final_img = Image.open(text_image_path)
    enlarged_img = Image.new("RGBA", (final_img.width + avatar_size+20, final_img.height), (0, 0, 0, 0))
    enlarged_img.paste(final_img, (avatar_size+20, 0))

    # Выбираем рандомное изображение из папки "avatars"
    avatars_dir = "avatars"
    avatars = [f for f in os.listdir(avatars_dir) if os.path.isfile(os.path.join(avatars_dir, f))]
    if avatars:
        random_avatar = random.choice(avatars)
        avatar_path = os.path.join(avatars_dir, random_avatar)

        # Открываем и вставляем аватар
        avatar_size = (avatar_size, avatar_size)
        avatar_img = Image.open(avatar_path).resize(avatar_size)
        avatar_img = avatar_img.convert("RGBA")

        # Создаем маску для аватара в форме круга
        avatar_mask = Image.new("L", avatar_size, 0)
        draw_mask = ImageDraw.Draw(avatar_mask)
        draw_mask.ellipse((0, 0, *avatar_size), fill=255)

        # Обрезаем аватар по маске и вставляем в увеличенное изображение
        avatar_img = Image.alpha_composite(Image.new("RGBA", avatar_size, (0, 0, 0, 0)), avatar_img)
        enlarged_img.paste(avatar_img, (5, 5), avatar_mask)

    # Сохраняем окончательное изображение
    if os.path.exists(text_image_path):
        os.remove(text_image_path)

    final_image_path = "final_image_with_avatar.png"
    enlarged_img.save(final_image_path, "PNG")

    return final_image_path


class CreateMovie():

    @classmethod
    def CreateMP4(cls, post_data):

        clips = []
        for post in post_data:
            clip = VideoFileClip(post['image_path']) if "gif" in post['image_path'] else ImageClip(post['image_path'])
            clip = clip.subclip(0, 12) if "gif" in post['image_path'] else clip.set_duration(12)

            bg_clip = clip.resize(newsize=(1080, 1920))
            bg_clip = bg_clip.fl_image(lambda img: cv2.blur(img, (21, 21)))

            if clip.size[1] / clip.size[0] > 1920 / 1080:
                fg_clip = clip.resize(height=1920)
            else:
                fg_clip = clip.resize(width=1080)
            fg_clip = fg_clip.set_position(("center", "center"))

            composite_clip = CompositeVideoClip([bg_clip, fg_clip], size=(1080, 1920))
            clips.append(composite_clip)
    
        clip = concatenate_videoclips(clips)
        clip = clip.subclip(0,60)

        colors = ['yellow', 'LightGreen', 'LightSkyBlue', 'LightPink4', 'SkyBlue2', 'MintCream','LimeGreen', 'WhiteSmoke', 'HotPink4']
        colors = colors + ['PeachPuff3', 'OrangeRed3', 'silver']
        random.shuffle(colors)
        text_clips = []
        notification_sounds = []
        
        for i, post in enumerate(post_data):
            if "![gif]" not in post['Best_comment']:
                return_comment, return_count = add_return_comment(post['Best_comment'])
                text_path = create_text_image(return_comment, os.path.join(os.getcwd(), 'core', 'Caprasimo-Regular.ttf'), 38)
                text_clip = ImageClip(text_path).set_duration(7).set_position((5, 500)).set_start((0, 3 + (i * 12)))
                text_clips.append(text_clip)

            # Создание плашки с текстом для ответа
            return_comment, _ = add_return_comment(post['best_reply'])
            if "![gif]" not in return_comment:
                text_path =create_text_image(return_comment, os.path.join(os.getcwd(), 'core', 'Caprasimo-Regular.ttf'), 38)
                text_clip = ImageClip(text_path).set_duration(7).set_position((5, 585 + (return_count * 50))).set_start((0, 5 + (i * 12)))
                text_clips.append(text_clip)

            notification = AudioFileClip(os.path.join(music_path, "notification.mp3")).set_start((0, 3 + (i * 12)))
            notification_sounds.append(notification)
            notification = AudioFileClip(os.path.join(music_path, "notification.mp3")).set_start((0, 5 + (i * 12)))
            notification_sounds.append(notification)
        
        music_file = os.path.join(music_path, f"music{random.randint(0,4)}.mp3")
        music = AudioFileClip(music_file)
        music = music.set_start((0,0))
        music = music.volumex(.4)
        music = music.set_duration(59)

        new_audioclip = CompositeAudioClip([music]+notification_sounds)
        clip.write_videofile(f"video_clips.mp4", fps = 24)
        
        clip = VideoFileClip("video_clips.mp4",audio=False)
        clip = CompositeVideoClip([clip] + text_clips)
        clip.audio = new_audioclip
        clip.write_videofile("video.mp4", fps=24)
        
        final_image_path = "./final_image_with_avatar.png"
        if os.path.exists(final_image_path):
            os.remove(final_image_path)

        if os.path.exists(os.path.join(dir_path, "video_clips.mp4")):
            os.remove(os.path.join(dir_path, "video_clips.mp4"))
        else:
            print(os.path.join(dir_path, "video_clips.mp4"))

if __name__ == '__main__':
    print(TextClip.list('color'))