import re, os, time
id_pattern = re.compile(r'^.\d+$')

class Config(object):
    # pyro client config
    API_ID    = os.environ.get("API_ID", "29917436")
    API_HASH  = os.environ.get("API_HASH", "4a926822b076a086a167fe8f2701d3e9")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "6936293249:AAFvRbk5JjERXqkVT3QXbjtE7FihwrzqYf0")

    # database config
    DB_NAME = os.environ.get("DB_NAME","AshutoshGoswami24")
    DB_URL  = os.environ.get("DB_URL","mongodb+srv://autoranembot:47lRvGstRz0DmA4w@cluster0.r7wan0y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    API  = os.environ.get("API","")

    # other configs
    BOT_UPTIME  = time.time()
    START_PIC   = os.environ.get("START_PIC", "https://graph.org/file/b372b3773e70fb60132c0.jpg")
    ADMIN       = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6141937812').split()]
    FORCE_SUB   = os.environ.get("FORCE_SUB", "pandawep")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001869105126"))
    FLOG_CHANNAL = int(os.environ.get("FLOG_CHANNAL", "-1002112731266"))

    # wes response configuration
    WEBHOOK = bool(os.environ.get("WEBHOOK", "True"))


class Txt(object):
    # part of text configuration

    START_TXT = """<b>Hello {}

➻ This Is An Advanced And Yet Powerful Rename Bot.

➻ Using This Bot You Can Auto Rename Of Your Files.

➻ This Bot Also Supports Custom Thumbnail And Custom Caption.

➻ Use /tutorial Command To Know How To Use Me.

Bot Is Made By @PandaWep

</b>
"""
#<b><a href='https://github.com/AshutoshGoswami24/Auto-Rename-Bot'>AshutoshGoswami24/Auto-Rename-Bot.git</a></b>
    FILE_NAME_TXT = """<b><u>SETUP AUTO RENAME FORMAT</u></b>

Use These Keywords To Setup Custom File Name

✓ episode :- To Replace Episode Number
✓ quality :- To Replace Video Resolution

<b>➻ Example :</b> <code> /autorename Naruto Shippuden S02 - EPepisode - quality  [Dual Audio] - @PandaWep </code>

<b>➻ Your Current Auto Rename Format :</b> <code>{format_template}</code> """

    ABOUT_TXT = f"""<b>🤖 My Name :</b>
<b>📝 Language :</b> <a href='https://python.org'>Python 3</a>
<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram 2.0</a>
<b>🚀 Server :</b> <a href='https://heroku.com'>Heroku</a>
<b>📢 Channel :</b> <a href='https://t.me/PandaWep'>PandaWep</a>
<b>🧑‍💻 Developer :</b> <a href='https://t.me/PandaWep'>PandaWep</a>

<b>♻️ Bot Made By :</b> @PandaWep"""


    THUMBNAIL_TXT = """<b><u>🖼️  HOW TO SET THUMBNAIL</u></b>

⦿ You Can Add Custom Thumbnail Simply By Sending A Photo To Me....

⦿ /viewthumb - Use This Command To See Your Thumbnail
⦿ /delthumb - Use This Command To Delete Your Thumbnail"""

    CAPTION_TXT = """<b><u>📝  HOW TO SET CAPTION</u></b>

⦿ /set_caption - Use This Command To Set Your Caption
⦿ /see_caption - Use This Command To See Your Caption
⦿ /del_caption - Use This Command To Delete Your Caption"""

    PROGRESS_BAR = """<b>\n
╭━━━━❰ᴘʀᴏɢʀᴇss ʙᴀʀ❱━➣
┣⪼ 🗃️ Sɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ Dᴏɴᴇ : {0}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ Eᴛᴀ: {4}
┣⪼ 🥺 joine Plz: @PandaWep
╰━━━━━━━━━━━━━━━➣ 
||<a href=https://t.me/botzpwchat>❏ If Speed Are not Fast Then Our Minimum Speed - 6MbPs 🚀 | 12MbPs 🚀 Then Plz Report Send on @botzpwchat</a>||
</b>"""


    DONATE_TXT = """<b>🥲 Thanks For Showing Interest In Donation! ❤️</b>

If You Like My Bots & Projects, You Can 🎁 Donate Me Any Amount From 10 Rs Upto Your Choice.

<b>My UPI - `PandaWep@ybl`</b>"""

    HELP_TXT = """<b>Hey</b> {}

Joine @PandaWep To Help """





# Jishu Developer
# Don't Remove Credit 🥺
# Telegram Channel @PandaWep
# Developer @AshutoshGoswami24
