from discord.ext import commands
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation
import datetime
import random
import cnlunar

def get_element_multipliers(user_ele, daily_ele):
    if user_ele == daily_ele:
        return {"cul": 1.5}
    restrained = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    if restrained.get(user_ele) == daily_ele:
        return {"cul": 0.75}
    mutual = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    if mutual.get(user_ele) == daily_ele:
        return {"cul": 2.0}
    return {"cul": 1.0}

class CultivateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cul', aliases=['xl', 'sit'])
    async def cultivate(self, ctx):
        """Command for cultivating"""
        try:
            user_id = str(ctx.author.id)
            user_collection = get_collection('users')
            timing_collection = get_collection('timings')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"
        except DatabaseError:
            await ctx.send("Database Error! Contact Bot admins!")
            return

        if not user:
            rtype, text = get_response('no_account', user=ctx.author.mention, lang=user_lang)
            await ctx.send(text)
            return

        if user.get('state', False):
            rtype, text = get_response('train_in_progress', user=user['in_game_username'], lang=user_lang)
            await ctx.send(text)
            return

        base_culti_gain = random.randint(150, 250)

        now_dt = datetime.datetime.now()
        lunar_date = datetime.datetime(now_dt.year, now_dt.month, now_dt.day, now_dt.hour, now_dt.minute)
        lunar = cnlunar.Lunar(lunar_date, godType="8char")
        elements_list = lunar.get_today5Elements()
        daily_element = None
        for word in elements_list:
            if word.startswith("属"):
                daily_element = word[1:]
                break
        if daily_element is None:
            daily_element = "未知"

        user_ele = user.get("element", None)
        if user_ele is None:
            multiplier = 1.0
        else:
            multiplier = get_element_multipliers(user_ele, daily_element)["cul"]

        actual_culti_gain = int(base_culti_gain * multiplier)

        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(hours=2)
        user_collection.update_one({"user_id": user_id}, {"$set": {"state": True}})

        timing_collection.insert_one({
            "user_id": user_id,
            "start_time": int(start_time.timestamp()),
            "end_time": int(end_time.timestamp()),
            "type": "cultivation",
            "culti_gain": actual_culti_gain
        })

        rtype, text = get_response(
            'cultivation_start',
            user=user['in_game_username'],
            end_time=f"<t:{int(end_time.timestamp())}:R>",
            culti_gain=actual_culti_gain,
            lang=user_lang
        )
        await ctx.send(text)

async def setup(bot):
    await bot.add_cog(CultivateCommand(bot))
