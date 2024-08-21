from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaDocument, Message
from PIL import Image
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.utils import progress_for_pyrogram, humanbytes, convert
from helper.database import AshutoshGoswami24
from config import Config
import os
import time
import re
import subprocess
import asyncio

renaming_operations = {}

# Pattern 1: S01E02 or S01EP02
pattern1 = re.compile(r"S(\d+)(?:E|EP)(\d+)")
# Pattern 2: S01 E02 or S01 EP02 or S01 - E01 or S01 - EP02
pattern2 = re.compile(r"S(\d+)\s*(?:E|EP|-\s*EP)(\d+)")
# Pattern 3: Episode Number After "E" or "EP"
pattern3 = re.compile(r"(?:[([<{]?\s*(?:E|EP)\s*(\d+)\s*[)\]>}]?)")
# Pattern 3_2: episode number after - [hyphen]
pattern3_2 = re.compile(r"(?:\s*-\s*(\d+)\s*)")
# Pattern 4: S2 09 ex.
pattern4 = re.compile(r"S(\d+)[^\d]*(\d+)", re.IGNORECASE)
# Pattern X: Standalone Episode Number
patternX = re.compile(r"(\d+)")
# QUALITY PATTERNS
# Pattern 5: 3-4 digits before 'p' as quality
pattern5 = re.compile(r"\b(?:.*?(\d{3,4}[^\dp]*p).*?|.*?(\d{3,4}p))\b", re.IGNORECASE)
# Pattern 6: Find 4k in brackets or parentheses
pattern6 = re.compile(r"[([<{]?\s*4k\s*[)\]>}]?", re.IGNORECASE)
# Pattern 7: Find 2k in brackets or parentheses
pattern7 = re.compile(r"[([<{]?\s*2k\s*[)\]>}]?", re.IGNORECASE)
# Pattern 8: Find HdRip without spaces
pattern8 = re.compile(r"[([<{]?\s*HdRip\s*[)\]>}]?|\bHdRip\b", re.IGNORECASE)
# Pattern 9: Find 4kX264 in brackets or parentheses
pattern9 = re.compile(r"[([<{]?\s*4kX264\s*[)\]>}]?", re.IGNORECASE)
# Pattern 10: Find 4kx265 in brackets or parentheses
pattern10 = re.compile(r"[([<{]?\s*4kx265\s*[)\]>}]?", re.IGNORECASE)


def extract_quality(filename):
    # Try Quality Patterns
    match5 = re.search(pattern5, filename)
    if match5:
        print("Matched Pattern 5")
        quality5 = match5.group(1) or match5.group(
            2
        )  # Extracted quality from both patterns
        print(f"Quality: {quality5}")
        return quality5

    match6 = re.search(pattern6, filename)
    if match6:
        print("Matched Pattern 6")
        quality6 = "4k"
        print(f"Quality: {quality6}")
        return quality6

    match7 = re.search(pattern7, filename)
    if match7:
        print("Matched Pattern 7")
        quality7 = "2k"
        print(f"Quality: {quality7}")
        return quality7

    match8 = re.search(pattern8, filename)
    if match8:
        print("Matched Pattern 8")
        quality8 = "HdRip"
        print(f"Quality: {quality8}")
        return quality8

    match9 = re.search(pattern9, filename)
    if match9:
        print("Matched Pattern 9")
        quality9 = "4kX264"
        print(f"Quality: {quality9}")
        return quality9

    match10 = re.search(pattern10, filename)
    if match10:
        print("Matched Pattern 10")
        quality10 = "4kx265"
        print(f"Quality: {quality10}")
        return quality10

    # Return "Unknown" if no pattern matches
    unknown_quality = "Unknown"
    print(f"Quality: {unknown_quality}")
    return unknown_quality


def extract_episode_number(filename):
    # Try Pattern 1
    match = re.search(pattern1, filename)
    if match:
        print("Matched Pattern 1")
        return match.group(2)  # Extracted episode number

    # Try Pattern 2
    match = re.search(pattern2, filename)
    if match:
        print("Matched Pattern 2")
        return match.group(2)  # Extracted episode number

    # Try Pattern 3
    match = re.search(pattern3, filename)
    if match:
        print("Matched Pattern 3")
        return match.group(1)  # Extracted episode number

    # Try Pattern 3_2
    match = re.search(pattern3_2, filename)
    if match:
        print("Matched Pattern 3_2")
        return match.group(1)  # Extracted episode number

    # Try Pattern 4
    match = re.search(pattern4, filename)
    if match:
        print("Matched Pattern 4")
        return match.group(2)  # Extracted episode number

    # Try Pattern X
    match = re.search(patternX, filename)
    if match:
        print("Matched Pattern X")
        return match.group(1)  # Extracted episode number

    # Return None if no pattern matches
    return None


# Example Usage:
filename = "Naruto Shippuden S01[episode] [quality][Dual Audio] @AshutoshGoswami24.mkv"
episode_number = extract_episode_number(filename)
print(f"Extracted Episode Number: {episode_number}")


@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def auto_rename_files(client, message):
    user_id = message.from_user.id
    format_template = await AshutoshGoswami24.get_format_template(user_id)
    media_preference = await AshutoshGoswami24.get_media_preference(user_id)

    if not format_template:
        return await message.reply_text(
            "Please Set An Auto Rename Format First Using /autorename"
        )

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        media_type = media_preference or "document"
    elif message.video:
        file_id = message.video.file_id
        file_name = f"{message.video.file_name}.mp4"
        media_type = media_preference or "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = f"{message.audio.file_name}.mp3"
        media_type = media_preference or "audio"
    else:
        return await message.reply_text("Unsupported File Type")

    if file_id in renaming_operations:
        elapsed_time = (datetime.now() - renaming_operations[file_id]).seconds
        if elapsed_time < 10:
            return

    renaming_operations[file_id] = datetime.now()

    episode_number = extract_episode_number(file_name)
    if episode_number:
        format_template = format_template.replace(
            "[episode]", "EP" + str(episode_number), 1
        )

        quality = extract_quality(file_name)
        format_template = format_template.replace("[quality]", quality)

    _, file_extension = os.path.splitext(file_name)
    renamed_file_name = f"{format_template}{file_extension}"
    renamed_file_path = f"downloads/{renamed_file_name}"
    metadata_file_path = f"Metadata/{renamed_file_name}"
    os.makedirs(os.path.dirname(renamed_file_path), exist_ok=True)
    os.makedirs(os.path.dirname(metadata_file_path), exist_ok=True)

    download_msg = await message.reply_text("Downloading the file...")

    try:
        path = await client.download_media(
            message,
            file_name=renamed_file_path,
            progress=progress_for_pyrogram,
            progress_args=("Download Started...", download_msg, time.time()),
        )
    except Exception as e:
        del renaming_operations[file_id]
        return await download_msg.edit(f"**Download Error:** {e}")

    await download_msg.edit("Renaming and Adding Metadata...")

    try:
        # Rename the file first
        os.rename(path, renamed_file_path)
        path = renamed_file_path

        # Add metadata if needed
        metadata_added = False
        _bool_metadata = await AshutoshGoswami24.get_metadata(user_id)
        if _bool_metadata:
            metadata = await AshutoshGoswami24.get_metadata_code(user_id)
            if metadata:
                cmd = f'ffmpeg -i "{renamed_file_path}"  -map 0 -c:s copy -c:a copy -c:v copy -metadata title="{metadata}" -metadata author="{metadata}" -metadata:s:s title="{metadata}" -metadata:s:a title="{metadata}" -metadata:s:v title="{metadata}"  "{metadata_file_path}"'
                try:
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, stderr = await process.communicate()
                    if process.returncode == 0:
                        metadata_added = True
                        path = metadata_file_path
                    else:
                        error_message = stderr.decode()
                        await download_msg.edit(f"**Metadata Error:**\n{error_message}")
                except asyncio.TimeoutError:
                    await download_msg.edit("**ffmpeg command timed out.**")
                    return
                except Exception as e:
                    await download_msg.edit(f"**Exception occurred:**\n{str(e)}")
                    return
        else:
            metadata_added = True

        if not metadata_added:
            # Metadata addition failed; upload the renamed file only
            await download_msg.edit(
                "Metadata addition failed. Uploading the renamed file only."
            )
            path = renamed_file_path

        # Upload the file
        upload_msg = await download_msg.edit("Uploading the file...")

        ph_path = None
        c_caption = await AshutoshGoswami24.get_caption(message.chat.id)
        c_thumb = await AshutoshGoswami24.get_thumbnail(message.chat.id)

        caption = (
            c_caption.format(
                filename=renamed_file_name,
                filesize=humanbytes(message.document.file_size),
                duration=convert(0),
            )
            if c_caption
            else f"**{renamed_file_name}**"
        )

        if c_thumb:
            ph_path = await client.download_media(c_thumb)
        elif media_type == "video" and message.video.thumbs:
            ph_path = await client.download_media(message.video.thumbs[0].file_id)

        if ph_path:
            img = Image.open(ph_path).convert("RGB")
            img = img.resize((320, 320))
            img.save(ph_path, "JPEG")

        try:
            if media_type == "document":
                await client.send_document(
                    message.chat.id,
                    document=path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("Upload Started...", upload_msg, time.time()),
                )
            elif media_type == "video":
                await client.send_video(
                    message.chat.id,
                    video=path,
                    caption=caption,
                    thumb=ph_path,
                    duration=0,
                    progress=progress_for_pyrogram,
                    progress_args=("Upload Started...", upload_msg, time.time()),
                )
            elif media_type == "audio":
                await client.send_audio(
                    message.chat.id,
                    audio=path,
                    caption=caption,
                    thumb=ph_path,
                    duration=0,
                    progress=progress_for_pyrogram,
                    progress_args=("Upload Started...", upload_msg, time.time()),
                )
        except Exception as e:
            os.remove(path)
            if ph_path:
                os.remove(ph_path)
            return await upload_msg.edit(f"**Upload Error:** {e}")

        # await upload_msg.edit("Upload Complete ✅")

    except Exception as e:
        await download_msg.edit(f"**Error:** {e}")

    finally:
        # Clean up
        if os.path.exists(renamed_file_path):
            os.remove(renamed_file_path)
        if os.path.exists(metadata_file_path):
            os.remove(metadata_file_path)
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)
        del renaming_operations[file_id]
