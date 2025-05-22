import discord
from discord.ext import commands
from utils.database import connect_mongo, get_collection, ensure_defaults
from utils.localisations import get_response
import os
import asyncio
import datetime
import sys
from discord.ext import tasks
from utils.database import backup_users_data, backup_items_data

TOKEN = "<INSERT_DISCORD_TOKEN_HERE>"
VERSION = "OSBLTSDiscord_pre-3.0.2"

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

admin_ids = [1234567890]        # Users with admin command access
tester_ids = [1234567890]       # No use yet...

# Initialise bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='^', intents=intents)

bot.version = VERSION

bot.remove_command('help')
async def load_commands():

    for folder in ['commands/game', 'commands/general', 'commands/admin']:
        if not os.path.exists(folder):
            continue
        for file in os.listdir(folder):
            if file.endswith('.py'):
                module = f"{folder.replace('/', '.')}.{file[:-3]}"
                try:
                    await bot.load_extension(module)
                    print(f"Loaded extension: {module}")
                except Exception as e:
                    print(f"Failed to load {module}: {e}")

async def check_cultivation_end():
    await bot.wait_until_ready()
    user_collection = get_collection("users")
    timing_collection = get_collection("timings")

    while not bot.is_closed():
        current_time = int(datetime.datetime.now().timestamp())
        ended_cultivations = timing_collection.find({"end_time": {"$lte": current_time}, "type": "cultivation"})

        for record in ended_cultivations:
            user_id = record["user_id"]
            user = user_collection.find_one({"user_id": user_id})
            if user and user.get("state"):
                culti_gain = record["culti_gain"]
                user_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"state": False}, "$inc": {"exp": culti_gain}}
                )
                try:
                    user_lang = user.get("lang", "CHS")
                    _, text = get_response('cultivation_end', lang=user_lang, culti_gain=culti_gain)
                    user_obj = await bot.fetch_user(int(user_id))
                    if user_obj:
                        await user_obj.send(text)
                except Exception as e:
                    print(f"Failed to send DM to user {user_id}: {e}")

            timing_collection.delete_one({"_id": record["_id"]})

        await asyncio.sleep(60) 

@tasks.loop(hours=1)        # Hourly backup, change to other timing if needed
async def auto_backup_users():
    users_backup = backup_users_data()
    items_backup = backup_items_data()
    if users_backup and items_backup:
        print(f"Auto-backup successful. Users: {users_backup}, Items: {items_backup}")
    else:
        print("Auto-backup failed.")

@auto_backup_users.before_loop
async def before_auto_backup_users():
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    print("!!!This is a free bot emulator, if you purchased for it, you have been scammed, please ask for refunds!!!")
    print(f"Bot has logged in as {bot.user}")
    connect_mongo()

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="out for errors"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

    # IMPORTANT: Dont Delete
    # Attempt to sync the slash commands globally and in a specific guild (Idk how it actually works but slash commands not synced or bugged without this)
    try:
        synced_global = await bot.tree.sync()
        print(f"Global: Synced {len(synced_global)} slash commands.")

        # Local sync:
        test_guild_id = 1234567890          # Enter your guild ID here
        synced_guild = await bot.tree.sync(guild=discord.Object(id=test_guild_id))
        print(f"Guild {test_guild_id}: Synced {len(synced_guild)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()

    raw_commands = {
        "开始": "start",
        "注册": "start",
        "状态": "stat",
        "测试": "test",
        "介绍": "intro",
        "修炼": "cul",
        "修仙": "cul",
        "打坐": "cul",
        "突破": "asc",
        "渡劫": "asc",
        "升阶": "asc",
        "签到": "daily",
        "每日": "daily",
        "打野": "wild",
        "打猎": "wild",
        "狩猎": "wild",
        "版本": "ver",
        "版本信息": "ver",
        "物品": "inv",
        "物品栏": "inv",
        "帮助": "help",
        "命令": "help",
        "指令": "help",
        "商店": "shop",
        "元素": "ele",
        "五行": "ele", 
        "联系": "contact",
    }
    if content in raw_commands:
        command_name = raw_commands[content]
        cmd = bot.get_command(command_name)
        if cmd:
            ctx = await bot.get_context(message)
            await ctx.invoke(cmd)
            return

    await bot.process_commands(message)

async def main():
    async with bot:
        await load_commands()
        connect_mongo()
        user_collection = get_collection("users")
        ensure_defaults(user_collection)
        auto_backup_users.start()
        bot.loop.create_task(check_cultivation_end())

        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())