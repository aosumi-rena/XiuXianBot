from discord.ext import commands
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation
import asyncio
import random
import datetime
import cnlunar

def get_element_multipliers(user_ele, daily_ele):
    if user_ele == daily_ele:
        return {"asc_fail": 8}
    restrained = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    if restrained.get(user_ele) == daily_ele:
        return {"asc_fail": 15}
    mutual = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    if mutual.get(user_ele) == daily_ele:
        return {"asc_fail": 10}
    return {"asc_fail": 10}

class AscendCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='asc', aliases=['ascend', 'tp', 'dj'])
    async def ascend(self, ctx):
        """Command for ascending."""
        try:
            user_id = str(ctx.author.id)
            user_collection = get_collection('users')
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

        current_stage = user.get('rank', 0)
        current_exp = user.get('exp', 0)
        textmap = load_localisation(user_lang)
        stage_max = int(textmap['xx_stage_max'].get(str(current_stage), 0))
        lightning_num = textmap['xx_stage_lightningNum'].get(str(current_stage + 1), 0)

        if current_exp < stage_max:
            rtype, text = get_response('insufficient_exp', lang=user_lang)
            await ctx.send(text)
            return

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
            multipliers = {"asc_fail": 10}
        else:
            multipliers = get_element_multipliers(user_ele, daily_element)

        asc_reduction = user.get('asc_reduction', 0)
        base_asc_fail = multipliers["asc_fail"]
        chance_of_failure = max(0, base_asc_fail - asc_reduction)

        if lightning_num == 0:
            new_stage_description = textmap['xx_stage_descriptions'].get(str(current_stage + 1), "ERROR")
            rtype, text = get_response(
                'ascend_success',
                user_ingame_name=user['in_game_username'],
                new_stage_description=new_stage_description,
                lang=user_lang
            )
            user_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"rank": 1}, "$set": {"exp": current_exp - stage_max}}
            )
            await ctx.send(text)
            return

        failed = False
        for i in range(1, lightning_num + 1):
            await asyncio.sleep(2)
            is_safe = random.randint(1, 100) > chance_of_failure
            condition = "condition_safe" if is_safe else "condition_failed"
            condition_text = textmap['responses'].get(condition, {}).get('text', "ERROR")
            rtype, text = get_response(
                'lightning_progress',
                lightningNum=i,
                user_ingame_name=user['in_game_username'],
                condition=condition_text,
                lang=user_lang
            )
            await ctx.send(text)
            if not is_safe:
                failed = True
                break

        if failed:
            rtype, text = get_response(
                'ascend_fail',
                user_ingame_name=user['in_game_username'],
                lang=user_lang
            )
            user_collection.update_one(
                {"user_id": user_id},
                {"$set": {"state": False}, "$inc": {"exp": -int(current_exp * 0.5)}}
            )
            await ctx.send(text)
        else:
            new_stage_description = textmap['xx_stage_descriptions'].get(str(current_stage + 1), "NO_TEXT(StageID_Description)")
            rtype, text = get_response(
                'ascend_success',
                user_ingame_name=user['in_game_username'],
                new_stage_description=new_stage_description,
                lang=user_lang
            )
            user_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"rank": 1}, "$set": {"exp": current_exp - stage_max}}
            )
            await ctx.send(text)

async def setup(bot):
    await bot.add_cog(AscendCommand(bot))
