from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from helper.database import AshutoshGoswami24
from pyromod.exceptions import ListenerTimeout
from config import Txt, Config


# AUTH_USERS = Config.AUTH_USERS

ON = [
    [InlineKeyboardButton("Metadata On ✅", callback_data="metadata_1")],
    [InlineKeyboardButton("Set Custom Metadata", callback_data="cutom_metadata")],
]
OFF = [
    [InlineKeyboardButton("Metadata Off ❌", callback_data="metadata_0")],
    [InlineKeyboardButton("Set Custom Metadata", callback_data="cutom_metadata")],
]


@Client.on_message(filters.private & filters.command("metadata"))
async def handle_metadata(bot: Client, message: Message):

    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    bool_metadata = await AshutoshGoswami24.get_metadata(message.from_user.id)
    user_metadata = await AshutoshGoswami24.get_metadata_code(message.from_user.id)
    await ms.delete()
    if bool_metadata:

        return await message.reply_text(
            f"<b>Your Current Metadata:</b>\n\n➜ `{user_metadata}` ",
            reply_markup=InlineKeyboardMarkup(ON),
        )

    return await message.reply_text(
        f"<b>Your Current Metadata:</b>\n\n➜ `{user_metadata}` ",
        reply_markup=InlineKeyboardMarkup(OFF),
    )


@Client.on_callback_query(filters.regex(".*?(custom_metadata|metadata).*?"))
async def query_metadata(bot: Client, query: CallbackQuery):

    data = query.data

    if data.startswith("metadata_"):
        _bool = data.split("_")[1]
        user_metadata = await AshutoshGoswami24.get_metadata_code(query.from_user.id)

        if bool(eval(_bool)):
            await AshutoshGoswami24.set_metadata(query.from_user.id, bool_meta=False)
            await query.message.edit(
                f"<b>Your Current Metadata:</b>\n\n➜ `{user_metadata}` ",
                reply_markup=InlineKeyboardMarkup(OFF),
            )

        else:
            await AshutoshGoswami24.set_metadata(query.from_user.id, bool_meta=True)
            await query.message.edit(
                f"<b>Your Current Metadata:</b>\n\n➜ `{user_metadata}` ",
                reply_markup=InlineKeyboardMarkup(ON),
            )

    elif data == "cutom_metadata":
        await query.message.delete()
        try:
            try:
                metadata = await bot.ask(
                    text=Txt.SEND_METADATA,
                    chat_id=query.from_user.id,
                    filters=filters.text,
                    timeout=30,
                    disable_web_page_preview=True,
                )
            except ListenerTimeout:
                await query.message.reply_text(
                    "⚠️ Error!!\n\n**Request timed out.**\nRestart by using /metadata",
                    reply_to_message_id=query.message.id,
                )
                return
            print(metadata.text)
            ms = await query.message.reply_text(
                "**Please Wait...**", reply_to_message_id=metadata.id
            )
            await AshutoshGoswami24.set_metadata_code(
                query.from_user.id, metadata_code=metadata.text
            )
            await ms.edit("**Your Metadta Code Set Successfully ✅**")
        except Exception as e:
            print(e)
