import asyncio
import aiohttp
from datetime import datetime, timedelta
from pytz import timezone
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from route import web_server

# Redeploy hook URL
REDEPLOY_HOOK_URL = Config.API
TRAFFIC_THRESHOLD = 100  # Set your threshold for high traffic
RATE_LIMIT = 10  # Number of messages per minute allowed per user
rate_limit_users = {}
traffic_counter = 0

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="renamer",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=50,  # Reduce the number of workers to minimize concurrent operations
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = Config.BOT_UPTIME     
        if Config.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()       
            await web.TCPSite(app, "0.0.0.0", 8080).start()     
        print(f"{me.first_name} Is Started.....✨️")
        for id in Config.ADMIN:
            try:
                await self.send_message(Config.LOG_CHANNEL, f"**{me.first_name} Is Started.....✨️**")                                
            except:
                pass
        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
                await self.send_message(Config.LOG_CHANNEL, f"**{me.mention} Is Restarted !!**\n\n📅 Date : `{date}`\n⏰ Time : `{time}`\n🌐 Timezone : `Asia/Kolkata`\n\n🉐 Version : `v{__version__} (Layer {layer})`</b>")                                
                await self.send_message(Config.FLOG_CHANNEL, f"{me.mention}-{time}")
            except:
                print("Please Make This Is Admin In Your Log Channel")

    async def on_message(self, message):
        global traffic_counter
        user_id = message.from_user.id
        current_time = datetime.now()

        if user_id in rate_limit_users:
            user_data = rate_limit_users[user_id]
            user_data['count'] += 1

            if user_data['count'] > RATE_LIMIT:
                if current_time - user_data['last_message'] < timedelta(minutes=1):
                    await message.reply_text("Rate limit exceeded. Please try again later.")
                    return
                else:
                    user_data['count'] = 1  # Reset count if more than a minute has passed
                    user_data['last_message'] = current_time
            else:
                user_data['last_message'] = current_time
        else:
            rate_limit_users[user_id] = {'count': 1, 'last_message': current_time}

        traffic_counter += 1
        if traffic_counter > TRAFFIC_THRESHOLD:
            await self.trigger_redeploy()
            traffic_counter = 0

        await self.process_message(message)

    async def trigger_redeploy(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(REDEPLOY_HOOK_URL) as response:
                if response.status == 200:
                    print("Triggered redeploy successfully.")
                else:
                    print(f"Failed to trigger redeploy: {response.status}")

Bot().run()


# from datetime import datetime
# from pytz import timezone
# from pyrogram import Client, __version__
# from pyrogram.raw.all import layer
# from config import Config
# from aiohttp import web
# from route import web_server

# class Bot(Client):

#     def __init__(self):
#         super().__init__(
#             name="renamer",
#             api_id=Config.API_ID,
#             api_hash=Config.API_HASH,
#             bot_token=Config.BOT_TOKEN,
#             workers=200,
#             plugins={"root": "plugins"},
#             sleep_threshold=15,
#         )

#     async def start(self):
#         await super().start()
#         me = await self.get_me()
#         self.mention = me.mention
#         self.username = me.username  
#         self.uptime = Config.BOT_UPTIME     
#         if Config.WEBHOOK:
#             app = web.AppRunner(await web_server())
#             await app.setup()       
#             await web.TCPSite(app, "0.0.0.0", 8080).start()     
#         print(f"{me.first_name} Is Started.....✨️")
#         for id in Config.ADMIN:
#             try: await self.send_message(Config.LOG_CHANNEL, f"**{me.first_name}  Is Started.....✨️**")                                
#             except: pass
#         if Config.LOG_CHANNEL:
#             try:
#                 curr = datetime.now(timezone("Asia/Kolkata"))
#                 date = curr.strftime('%d %B, %Y')
#                 time = curr.strftime('%I:%M:%S %p')
#                 await self.send_message(Config.LOG_CHANNEL, f"**{me.mention} Is Restarted !!**\n\n📅 Date : `{date}`\n⏰ Time : `{time}`\n🌐 Timezone : `Asia/Kolkata`\n\n🉐 Version : `v{__version__} (Layer {layer})`</b>")                                
#                 await self.send_message(Config.FLOG_CHANNEL, f"{me.mention}-{time}")
#             except:
#                 print("Please Make This Is Admin In Your Log Channel")

# Bot().run()



# from datetime import datetime
# from pytz import timezone
# from pyrogram import Client, __version__
# from pyrogram.raw.all import layer
# from config import Config
# from aiohttp import web
# from route import web_server

# class Bot(Client):
#     def __init__(self):
#         super().__init__(
#             name="renamer",
#             api_id=Config.API_ID,
#             api_hash=Config.API_HASH,
#             bot_token=Config.BOT_TOKEN,
#             workers=200,
#             plugins={"root": "plugins"},
#             sleep_threshold=15,
#         )

#     async def start(self):
#         await super().start()
#         me = await self.get_me()
#         self.mention = me.mention
#         self.username = me.username
#         self.uptime = Config.BOT_UPTIME
#         if Config.WEBHOOK:
#             app = web.Application()
#             app.router.add_route('GET', '/', web_server)
#             runner = web.AppRunner(app)
#             await runner.setup()
#             site = web.TCPSite(runner, "0.0.0.0", 8080)
#             await site.start()
#         print(f"{me.first_name} Is Started.....✨️")
#         for admin_id in Config.ADMIN:
#             try:
#                 await self.send_message(admin_id, f"**{me.first_name} Is Started.....✨️**")
#             except Exception as e:
#                 print(f"Error sending message to admin {admin_id}: {e}")
#         if Config.LOG_CHANNEL:
#             try:
#                 curr = datetime.now(timezone("Asia/Kolkata"))
#                 date = curr.strftime('%d %B, %Y')
#                 time = curr.strftime('%I:%M:%S %p')
#                 await self.send_message(Config.LOG_CHANNEL, f"**{me.mention} Is Restarted !!**\n\n📅 Date : `{date}`\n⏰ Time : `{time}`\n🌐 Timezone : `Asia/Kolkata`\n\n🉐 Version : `v{__version__} (Layer {layer})`</b>")
#                 await self.send_message(Config.FLOG_CHANNEL, f"{me.mention}-{time}")
#             except Exception as e:
#                 print(f"Error sending log message: {e}")

# if __name__ == "__main__":
#     Bot().run()




# from datetime import datetime
# from pytz import timezone
# from pyrogram import Client, __version__
# from pyrogram.raw.all import layer
# from config import Config
# from aiohttp import web
# from route import web_server

# class Bot(Client):

#     def __init__(self):
#         super().__init__(
#             name="renamer",
#             api_id=Config.API_ID,
#             api_hash=Config.API_HASH,
#             bot_token=Config.BOT_TOKEN,
#             workers=200,
#             plugins={"root": "plugins"},
#             sleep_threshold=15,
#         )

#     async def start(self):
#         await super().start()
#         me = await self.get_me()
#         self.mention = me.mention
#         self.username = me.username  
#         self.uptime = Config.BOT_UPTIME     
#         if Config.WEBHOOK:
#             app = web.AppRunner(await web_server())
#             await app.setup()       
#             await web.TCPSite(app, "0.0.0.0", 8080).start()     
#         print(f"{me.first_name} Is Started.....✨️")
#         for id in Config.ADMIN:
#             try: await self.send_message(Config.LOG_CHANNEL, f"**{me.first_name}  Is Started.....✨️**")                                
#             except: pass
#         if Config.LOG_CHANNEL:
#             try:
#                 curr = datetime.now(timezone("Asia/Kolkata"))
#                 date = curr.strftime('%d %B, %Y')
#                 time = curr.strftime('%I:%M:%S %p')
#                 await self.send_message(Config.LOG_CHANNEL, f"**{me.mention} Is Restarted !!**\n\n📅 Date : `{date}`\n⏰ Time : `{time}`\n🌐 Timezone : `Asia/Kolkata`\n\n🉐 Version : `v{__version__} (Layer {layer})`</b>")
#                 await self.send_message(Config.FLOG_CHANNAL, f"{me.mention}-{time}")
#             except:
#                 print("Please Make This Is Admin In Your Log Channel")

# Bot().run()



# # PandaWep
# # Don't Remove Credit 🥺
# # Telegram Channel @PandaWep
# # Developer https://github.com/PandaWep
