import discord
from discord.ext import commands
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation
import datetime
import random
import cnlunar

def get_element_multipliers(user_ele, daily_ele):
    if user_ele == daily_ele:
        return {
            "cul": 1.5,
            "hunt_copper": 2.0,
            "hunt_gold": 2.0,
            "hunt_cultivation": 1.0,
            "asc_fail": 8
        }
    restrained = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    if restrained.get(user_ele) == daily_ele:
        return {
            "cul": 0.75,
            "hunt_copper": 0.75,
            "hunt_gold": 1.0,
            "hunt_cultivation": 0.75,
            "asc_fail": 15
        }
    mutual = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    if mutual.get(user_ele) == daily_ele:
        return {
            "cul": 2.0,
            "hunt_copper": 1.5,
            "hunt_gold": 1.0,
            "hunt_cultivation": 2.0,
            "asc_fail": 10
        }
    return {
        "cul": 1.0,
        "hunt_copper": 1.0,
        "hunt_gold": 1.0,
        "hunt_cultivation": 1.0,
        "asc_fail": 10
    }

class HuntCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hunt', aliases=['wild', 'dy'])
    async def hunt(self, ctx):
        """Command for hunting."""
        user_id = str(ctx.author.id)
        try:
            user_collection = get_collection('users')
            timing_collection = get_collection('timings')
            user = user_collection.find_one({"user_id": user_id})
            if not user:
                rtype, text = get_response('no_account', user=ctx.author.mention, lang="CHS")
                await ctx.send(text)
                return
        except DatabaseError:
            await ctx.send("Database Error! Contact Bot admins!")
            return

        user_lang = user.get("lang", "CHS")
        user_ingame_name = user.get("in_game_username", ctx.author.display_name)
        if user.get('state', False):
            rtype, text = get_response('train_in_progress', user=user_ingame_name, lang=user_lang)
            await ctx.send(text)
            return

        timing = timing_collection.find_one({"user_id": user_id, "type": "hunt_cd"})
        current_time = int(datetime.datetime.now().timestamp())
        if timing and current_time < timing["end_time"]:
            rtype, text = get_response(
                'hunt_cooldown',
                user=user_ingame_name,
                remaining_time=f"<t:{timing['end_time']}:R>",
                lang=user_lang
            )
            await ctx.send(text)
            return

        stage = user.get('rank', 0)
        textmap = load_localisation(user_lang)
        stage_max_value = int(textmap['xx_stage_max'].get(str(stage), 0))

        if stage == 70:
            base_cultivation_gain = 0
        else:
            base_cultivation_gain = random.randint(int(stage_max_value * 0.0075), int(stage_max_value * 0.0125))
        base_copper_gain = random.randint(100, 200)
        base_yuanbao_gain = 0

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
            multipliers = {"cul": 1.0, "hunt_copper": 1.0, "hunt_gold": 1.0, "hunt_cultivation": 1.0, "asc_fail": 10}
        else:
            multipliers = get_element_multipliers(user_ele, daily_element)

        cultivation_gain = int(base_cultivation_gain * multipliers["hunt_cultivation"] * 1.0)
        copper_gain = int(base_copper_gain * multipliers["hunt_copper"] * 1.0)

        # Shitty logics...
        if stage < 14:
            if random.random() < 0.006:
                base_yuanbao_gain = 1
            elif random.random() < 0.006**2:
                base_yuanbao_gain = 2
            elif random.random() < 0.006**3:
                base_yuanbao_gain = 3
            elif random.random() < 0.006**4:
                base_yuanbao_gain = 4
            elif random.random() < 0.006**5:
                base_yuanbao_gain = 5000000
        elif 14 < stage < 23:
            if random.random() < 0.012:
                base_yuanbao_gain = 1
            elif random.random() < 0.012**2:
                base_yuanbao_gain = 2
            elif random.random() < 0.012**3:
                base_yuanbao_gain = 3
            elif random.random() < 0.012**4:
                base_yuanbao_gain = 4
            elif random.random() < 0.012**5:
                base_yuanbao_gain = 5
            elif random.random() < 0.006**5:
                base_yuanbao_gain = 5000000
        elif 23 <= stage <= 41:
            if random.random() <= 0.24:
                base_yuanbao_gain = 1
            elif random.random() < 0.24**2:
                base_yuanbao_gain = 2
            elif random.random() < 0.24**3:
                base_yuanbao_gain = 4
            elif random.random() < 0.24**4:
                base_yuanbao_gain = 6
            elif random.random() < 0.24**5:
                base_yuanbao_gain = 8
            elif random.random() < 0.24**6:
                base_yuanbao_gain = 16
            elif random.random() < 0.006**5:
                base_yuanbao_gain = 5000000
        elif stage >= 41:
            if random.random() <= 0.5:
                base_yuanbao_gain = 1
            elif random.random() < 0.5**2:
                base_yuanbao_gain = 2
            elif random.random() < 0.5**3:
                base_yuanbao_gain = 4
            elif random.random() < 0.5**4:
                base_yuanbao_gain = 6
            elif random.random() < 0.5**5:
                base_yuanbao_gain = 8
            elif random.random() < 0.5**6:
                base_yuanbao_gain = 16
            elif random.random() < 0.5**7:
                base_yuanbao_gain = 32
            elif random.random() < 0.5**8:
                base_yuanbao_gain = 64
            elif random.random() < 0.5**9:
                base_yuanbao_gain = 128
            elif random.random() < 0.5**10:
                base_yuanbao_gain = 256
            elif random.random() < 0.006**5:
                base_yuanbao_gain = 5000000

        yuanbao_gain = int(base_yuanbao_gain * multipliers["hunt_gold"] * 1.0)

        user_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"exp": cultivation_gain, "copper": copper_gain, "gold": yuanbao_gain, "dy_times": 1}}
        )

        timing_collection.update_one(
            {"user_id": user_id, "type": "hunt_cd"},
            {"$set": {"start_time": current_time, "end_time": current_time + 3600, "type": "hunt_cd"}},
            upsert=True
        )

        rtype, text = get_response(
            'hunt_success',
            user=user_ingame_name,
            cultivation_gain=cultivation_gain,
            copper_gain=copper_gain,
            yuanbao_gain=yuanbao_gain,
            lang=user_lang
        )
        if rtype == "embed":
            embed = discord.Embed(title="Hunting Rewards", description=text, color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            await ctx.send(text)

async def setup(bot):
    await bot.add_cog(HuntCommand(bot))
