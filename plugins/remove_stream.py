import os
import re
import json
import time
import asyncio
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# store user selections temporarily
user_data = {}


async def get_streams(file_path):
    cmd = f'ffprobe -v quiet -print_format json -show_streams -show_format "{file_path}"'
    result = subprocess.check_output(cmd, shell=True)
    data = json.loads(result)
    return data["streams"], data.get("format", {})


def build_buttons(uid):
    """Rebuild the keyboard with Audio/Subtitle sections separated and
    color-coded selection state:
      🟦 = section header (Video/Audio/Subtitle)
      🟩 = stream selected for removal
      🟥 = stream not selected
    """
    data = user_data[uid]
    streams = data["streams"]
    selected = data["selected"]

    buttons = []

    video_streams = [s for s in streams if s["codec_type"] == "video"]
    audio_streams = [s for s in streams if s["codec_type"] == "audio"]
    sub_streams = [s for s in streams if s["codec_type"] == "subtitle"]

    if video_streams:
        buttons.append([InlineKeyboardButton("🟦 Video", callback_data="noop")])
        for s in video_streams:
            buttons.append([_stream_button(s, selected)])

    if audio_streams:
        buttons.append([InlineKeyboardButton("🟦 Audio", callback_data="noop")])
        for s in audio_streams:
            buttons.append([_stream_button(s, selected)])

    if sub_streams:
        buttons.append([InlineKeyboardButton("🟦 Subtitle", callback_data="noop")])
        for s in sub_streams:
            buttons.append([_stream_button(s, selected)])

    buttons.append([InlineKeyboardButton("🟩 Remove Selected", callback_data="do_remove")])
    buttons.append([InlineKeyboardButton("🟥 Cancel", callback_data="cancel_remove")])
    return InlineKeyboardMarkup(buttons)


def _stream_button(s, selected):
    idx = s["index"]
    lang = s.get("tags", {}).get("language", "und")
    title = s.get("tags", {}).get("title", "")
    codec = s.get("codec_name", "")
    label = f"#{idx} {codec} ({lang})"
    if title:
        label += f" - {title}"
    mark = "🟩" if idx in selected else "🟥"
    return InlineKeyboardButton(f"{mark} {label}", callback_data=f"toggle_{idx}")


@Client.on_message(filters.command("removestream") & filters.reply)
async def remove_stream_start(client, message):
    reply = message.reply_to_message
    if not (reply.video or reply.document):
        return await message.reply("Video/file ku reply pannunga")

    status = await message.reply("📥 Downloading file...")
    file_path = await client.download_media(
        reply,
        progress=progress_for_pyrogram,
        progress_args=(status, "📥 Downloading", time.time()),
    )

    streams, fmt = await get_streams(file_path)

    user_data[message.from_user.id] = {
        "file": file_path,
        "streams": streams,
        "duration": float(fmt.get("duration", 0)),
        "selected": [],
        "status_msg": status,
    }

    await status.edit(
        "Select streams to remove:\n(🟩 selected / 🟥 not selected)",
        reply_markup=build_buttons(message.from_user.id),
    )


@Client.on_callback_query(filters.regex(r"^noop$"))
async def noop(client, callback_query):
    await callback_query.answer()


@Client.on_callback_query(filters.regex(r"^toggle_\d+$"))
async def toggle_stream(client, callback_query):
    idx = int(callback_query.data.split("_")[1])
    uid = callback_query.from_user.id
    if uid not in user_data:
        return await callback_query.answer("Session expired, /removestream mudhalla try pannunga.", show_alert=True)

    sel = user_data[uid]["selected"]
    if idx in sel:
        sel.remove(idx)
    else:
        sel.append(idx)

    await callback_query.message.edit_reply_markup(build_buttons(uid))
    await callback_query.answer(f"Stream #{idx} {'selected' if idx in sel else 'deselected'}")


@Client.on_callback_query(filters.regex("^cancel_remove$"))
async def cancel_remove(client, callback_query):
    uid = callback_query.from_user.id
    data = user_data.pop(uid, None)
    if data and os.path.exists(data["file"]):
        os.remove(data["file"])
    await callback_query.message.edit("🟥 Cancelled.")


@Client.on_callback_query(filters.regex("^do_remove$"))
async def do_remove(client, callback_query):
    uid = callback_query.from_user.id
    data = user_data.get(uid)
    if not data or not data["selected"]:
        return await callback_query.answer("Onnum select pannala!", show_alert=True)

    status = data["status_msg"]
    input_file = data["file"]
    output_file = input_file.rsplit(".", 1)[0] + "_edited." + input_file.rsplit(".", 1)[1]
    duration = data["duration"]

    map_cmd = " ".join([f"-map -0:{i}" for i in data["selected"]])
    cmd = (
        f'ffmpeg -y -i "{input_file}" -map 0 {map_cmd} -c copy '
        f'-progress pipe:1 -nostats "{output_file}"'
    )

    await status.edit("⚙️ Processing: 0%")
    await run_ffmpeg_with_progress(cmd, duration, status)

    await status.edit("📤 Uploading...")
    await client.send_document(
        callback_query.message.chat.id,
        output_file,
        progress=progress_for_pyrogram,
        progress_args=(status, "📤 Uploading", time.time()),
    )

    await status.delete()

    for f in (input_file, output_file):
        if os.path.exists(f):
            os.remove(f)
    del user_data[uid]


async def run_ffmpeg_with_progress(cmd, duration, status_msg):
    """Runs ffmpeg asynchronously and edits status_msg with a live % progress
    bar parsed from ffmpeg's -progress pipe:1 output."""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    last_edit = 0
    current_time = 0

    while True:
        line = await process.stdout.readline()
        if not line:
            break
        line = line.decode(errors="ignore").strip()

        if line.startswith("out_time_ms="):
            try:
                current_time = int(line.split("=")[1]) / 1_000_000
            except ValueError:
                continue

            if duration > 0:
                percent = min(current_time / duration * 100, 100)
                now = time.time()
                if now - last_edit > 3:  # throttle edits to avoid flood-wait
                    bar = make_progress_bar(percent)
                    try:
                        await status_msg.edit(f"⚙️ Processing:\n{bar} {percent:.1f}%")
                    except Exception:
                        pass
                    last_edit = now

        if line.startswith("progress=") and line.endswith("end"):
            break

    await process.wait()


def make_progress_bar(percent, length=12):
    filled = int(length * percent / 100)
    return "▰" * filled + "▱" * (length - filled)


async def progress_for_pyrogram(current, total, status_msg, action, start_time):
    now = time.time()
    if not hasattr(progress_for_pyrogram, "_last"):
        progress_for_pyrogram._last = {}
    key = id(status_msg)
    last = progress_for_pyrogram._last.get(key, 0)
    if now - last < 3 and current != total:
        return
    progress_for_pyrogram._last[key] = now

    percent = current * 100 / total
    bar = make_progress_bar(percent)
    speed = current / (now - start_time) if now > start_time else 0
    eta = (total - current) / speed if speed > 0 else 0

    try:
        await status_msg.edit(
            f"{action}:\n{bar} {percent:.1f}%\n"
            f"{humanbytes(current)} / {humanbytes(total)} | {humanbytes(speed)}/s | ETA {int(eta)}s"
        )
    except Exception:
        pass


def humanbytes(size):
    if not size:
        return "0B"
    power = 1024
    n = 0
    units = ["B", "KB", "MB", "GB", "TB"]
    while size > power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f}{units[n]}"
    
