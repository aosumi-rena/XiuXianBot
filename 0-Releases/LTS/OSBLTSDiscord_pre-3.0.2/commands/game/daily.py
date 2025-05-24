from discord.ext import commands, tasks
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response
import datetime
import time

class DailyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reset_sign_status.start()

    @commands.command(name='daily', aliases=['sign', 'qd'])
    async def daily(self, ctx):
        """Command for daily sign in."""
        try:
            user_id = str(ctx.author.id)
            user_collection = get_collection('users')

            user = user_collection.find_one({"user_id": user_id})
            if not user:
                response_type, text = get_response('no_account', user=ctx.author.mention, lang="CHS")
                await ctx.send(text)
                return
        except DatabaseError:
            await ctx.send(content="Database Error! Contact Bot admins!")

        user_lang = user.get("lang", "CHS")
        user_ingame_name = user.get("in_game_username", ctx.author.display_name)

        if user.get("sign", False):
            response_type, text = get_response('already_sign', user_ingame_name=user_ingame_name, lang=user_lang)
            await ctx.send(text)
            return

        user_collection.update_one(
            {"user_id": user_id},
            {"$set": {"sign": True}, "$inc": {"gold": 1, "copper": 500}}
        )

        response_type, text = get_response('sign_success', user_ingame_name=user_ingame_name, lang=user_lang)
        await ctx.send(text)

    @tasks.loop(minutes=1)
    async def reset_sign_status(self):
        user_collection = get_collection('users')
        timing_collection = get_collection('timings')

        last_reset = timing_collection.find_one({"type": "daily_reset"})
        last_reset_time = last_reset.get("timestamp", 0) if last_reset else 0
        current_time = int(time.time())

        now = datetime.datetime.now()
        if now.hour == 4 and now.minute == 0 or current_time - last_reset_time >= 86400:  # 24 hours
            user_collection.update_many({}, {"$set": {"sign": False}})

            timing_collection.update_one(
                {"type": "daily_reset"},
                {"$set": {"timestamp": current_time, "type": "daily_reset"}},
                upsert=True
            )
            print(f"Daily sign-in status reset successfully at {now.strftime('%Y-%m-%d %H:%M:%S')}.")

    @reset_sign_status.before_loop
    async def before_reset_sign_status(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DailyCommand(bot))