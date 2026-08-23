import os, json, subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# store user selections temporarily
user_data = {}

async def get_streams(file_path):
    cmd = f'ffprobe -v quiet -print_format json -show_streams "{file_path}"'
    result = subprocess.check_output(cmd, shell=True)
    return json.loads(result)["streams"]

@Client.on_message(filters.command("removestream") & filters.reply)
async def remove_stream_start(client, message):
    reply = message.reply_to_message
    if not (reply.video or reply.document):
        return await message.reply("Video/file ku reply pannunga")
    
    file_path = await client.download_media(reply)
    streams = await get_streams(file_path)
    
    user_data[message.from_user.id] = {"file": file_path, "selected": []}
    
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

@Client.on_callback_query(filters.regex(r"toggle_\d+"))
async def toggle_stream(client, callback_query):
    idx = int(callback_query.data.split("_")[1])
    uid = callback_query.from_user.id
    sel = user_data[uid]["selected"]
    if idx in sel:
        sel.remove(idx)
    else:
        sel.append(idx)
    await callback_query.answer(f"Stream {idx} {'selected' if idx in sel else 'deselected'}")

@Client.on_callback_query(filters.regex("do_remove"))
async def do_remove(client, callback_query):
    uid = callback_query.from_user.id
    data = user_data.get(uid)
    if not data or not data["selected"]:
        return await callback_query.answer("Onnum select pannala!", show_alert=True)
    
    input_file = data["file"]
    output_file = input_file.replace(".", "_edited.", 1)
    
    map_cmd = ' '.join([f'-map -0:{i}' for i in data["selected"]])
    cmd = f'ffmpeg -i "{input_file}" -map 0 {map_cmd} -c copy "{output_file}"'
    subprocess.run(cmd, shell=True)
    
    await client.send_document(callback_query.message.chat.id, output_file)
    
    # cleanup
    os.remove(input_file)
    os.remove(output_file)
    del user_data[uid]
