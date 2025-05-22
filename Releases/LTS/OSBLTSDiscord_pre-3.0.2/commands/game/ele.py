import discord
from discord.ext import commands
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation
import datetime
import cnlunar

class ElementCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ele", aliases=['element', 'ys', 'wx'])
    async def ele_command(self, ctx, subcommand: str = None, arg: str = None):
        """
        Usage:
          ^ele or ^ele check        -> Check today's element (computed via lunar info)
          ^ele choose               -> Show available elements (if your stage >= 14, not cultivating, and no cooldown)
          ^ele choose <choice>      -> Choose your element
        """
        user_id = str(ctx.author.id)
        try:
            user_collection = get_collection("users")
            timing_collection = get_collection("timings")
        except DatabaseError:
            await ctx.send("Database Error! Contact Bot admins!")
            return

        user = user_collection.find_one({"user_id": user_id})
        if not user:
            _, text = get_response("no_account", user=ctx.author.mention, lang="CHS")
            await ctx.send(text)
            return

        user_lang = user.get("lang", "CHS")
        stage = user.get("rank", 0)

        now = datetime.datetime.now()
        lunar_date = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
        lunar = cnlunar.Lunar(lunar_date, godType="8char")
        elements_list = lunar.get_today5Elements()
        daily_element = None
        for word in elements_list:
            if word.startswith("属"):
                daily_element = word[1:]  # Remove 属
                break
        if daily_element is None:
            daily_element = "未知"

        if user_lang.upper() != "CHS":
            ELEMENT_TRANSLATIONS = {
                "金": "Metallo",
                "木": "Dendro",
                "水": "Hydro",
                "火": "Pyro",
                "土": "Geo"
            }
            daily_element = ELEMENT_TRANSLATIONS.get(daily_element, daily_element)


        # --- Subcommand: check ---
        if subcommand is None or subcommand.lower() == "check":
            _, response_text = get_response("ele_check", lang=user_lang, daily_element=daily_element)
            embed = discord.Embed(
                title="Daily Element | 今日元素",
                description=response_text,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        # --- Subcommand: rule(s) ---
        if subcommand.lower() in ["rule", "rules"]:
            _, response_text = get_response("ele_rules", lang=user_lang)
            embed = discord.Embed(
                title="Element Buff Rules | 元素加成规则",
                description=response_text,
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            return

        # --- Subcommand: choose ---
        if subcommand.lower() == "choose":
            if user.get("state", False):
                _, response_text = get_response("ele_cannot_choose", lang=user_lang)
                await ctx.send(response_text)
                return

            if stage < 14:
                _, response_text = get_response("ele_stage_too_low", lang=user_lang, required_stage=14)
                await ctx.send(response_text)
                return

            current_time = int(datetime.datetime.now().timestamp())
            cd = timing_collection.find_one({"user_id": user_id, "type": "ele_cd"})
            if cd and current_time < cd["end_time"]:
                _, response_text = get_response("ele_cd_active", lang=user_lang, remaining_time=f"<t:{cd['end_time']}:R>")
                await ctx.send(response_text)
                return

            if arg is None:
                elements = {
                    "1": {"eng": "Metallo", "chs": "金", "short": "metallo"},
                    "2": {"eng": "Dendro", "chs": "木", "short": "dendro"},
                    "3": {"eng": "Hydro",  "chs": "水", "short": "hydro"},
                    "4": {"eng": "Pyro",   "chs": "火", "short": "pyro"},
                    "5": {"eng": "Geo",    "chs": "土", "short": "geo"}
                }
                lines = []
                for num, names in elements.items():
                    lines.append(f"{num}: {names['eng']} ({names['chs']})")
                available_text = "\n".join(lines)
                _, response_text = get_response("ele_choose_prompt", lang=user_lang, available=available_text)
                await ctx.send(response_text)
                return
            else:
                elements = {
                    "1": {"eng": "Metallo", "chs": "金", "short": "metallo"},
                    "2": {"eng": "Dendro", "chs": "木", "short": "dendro"},
                    "3": {"eng": "Hydro",  "chs": "水", "short": "hydro"},
                    "4": {"eng": "Pyro",   "chs": "火", "short": "pyro"},
                    "5": {"eng": "Geo",    "chs": "土", "short": "geo"}
                }
                chosen = None
                arg_lower = arg.lower()
                for key, names in elements.items():
                    if arg_lower == key or arg_lower == names["eng"].lower() or arg_lower == names["chs"] or arg_lower == names["short"]:
                        chosen = names["chs"]
                        break
                if not chosen:
                    _, response_text = get_response("ele_invalid_choice", lang=user_lang)
                    await ctx.send(response_text)
                    return

                user_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"element": chosen}}
                )
                # 30 day cd
                cooldown_seconds = 30 * 24 * 3600
                new_cd = {
                    "user_id": user_id,
                    "type": "ele_cd",
                    "start_time": current_time,
                    "end_time": current_time + cooldown_seconds
                }
                timing_collection.update_one(
                    {"user_id": user_id, "type": "ele_cd"},
                    {"$set": new_cd},
                    upsert=True
                )
                local_map = load_localisation(user_lang)
                if user_lang.upper() != "CHS":
                    display_chosen = local_map.get("elements", {}).get(chosen, chosen)
                else:
                    display_chosen = chosen
                _, response_text = get_response("ele_choose_success", lang=user_lang, chosen=display_chosen)
                await ctx.send(response_text)
                return
            
        _, response_text = get_response("ele_invalid_subcommand", lang=user_lang)
        await ctx.send(response_text)

async def setup(bot):
    await bot.add_cog(ElementCommand(bot))
