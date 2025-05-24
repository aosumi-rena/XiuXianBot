import discord
from discord.ext import commands
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation

class StatusCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='stat', aliases=['zt', 'status'])
    async def stat(self, ctx):
        """Command to check your current status."""
        try:
            user_id = str(ctx.author.id)
            user_collection = get_collection('users')
        except DatabaseError:
            await ctx.send(content="Database Error! Contact Bot admins!")
            return

        user = user_collection.find_one({"user_id": user_id})
        user_lang = user.get("lang", "CHS") if user else "CHS"

        if not user:
            response_type, text = get_response('no_account', user=ctx.author.mention, lang=user_lang)
            if response_type == "embed":
                embed = discord.Embed(title="NO_ACCOUNT", description=text, color=0xff0000)
                await ctx.send(embed=embed)
            else:
                await ctx.send(text)
            return

        element = user.get("element")
        if element is None:
            element = "无" if user_lang.upper() == "CHS" else "None"
        if user_lang.upper() != "CHS":
            ELEMENT_TRANSLATIONS = {
                "金": "Metallo",
                "木": "Dendro",
                "水": "Hydro",
                "火": "Pyro",
                "土": "Geo"
            }
            element = ELEMENT_TRANSLATIONS.get(element, element)

        in_game_username = user.get("in_game_username", ctx.author.mention)
        stage_description = load_localisation(user_lang)['xx_stage_descriptions'].get(str(user['rank']), "ERROR")
        max_exp = load_localisation(user_lang)['xx_stage_max'].get(str(user['rank']), "ERROR")

        response_type, text = get_response(
            'user_status',
            user=in_game_username,
            user_id=user_id,
            exp=user['exp'],
            rank=user['rank'],
            max_exp=max_exp,
            stage_description=stage_description,
            element=element,
            lang=user_lang
        )

        if response_type == "embed":
            embed = discord.Embed(title=f"{in_game_username}", description=text, color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            await ctx.send(text)

async def setup(bot):
    await bot.add_cog(StatusCommand(bot))
