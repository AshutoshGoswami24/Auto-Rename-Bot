import os, subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def get_streams(file_path):
    cmd = f'ffprobe -v quiet -print_format json -show_streams "{file_path}"'
    result = subprocess.check_output(cmd, shell=True)
    import json
    return json.loads(result)["streams"]

@Client.on_message(filters.command("removestream") & filters.reply)
async def remove_stream_start(client, message):
    reply = message.reply_to_message
    if not (reply.video or reply.document):
        return await message.reply("Video/file ku reply pannunga")
    
    file_path = await client.download_media(reply)
    streams = await get_streams(file_path)
    
    buttons = []
    for s in streams:
        idx = s["index"]
        lang = s.get("tags", {}).get("language", "und")
        buttons.append([InlineKeyboardButton(
            f"❌ {s['codec_type']} #{idx} ({lang})",
            callback_data=f"toggle_{idx}"
        )])
    buttons.append([InlineKeyboardButton("✅ Remove Selected", callback_data="do_remove")])
    
    await message.reply("Select streams to remove:", reply_markup=InlineKeyboardMarkup(buttons))
