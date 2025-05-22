import discord
from discord.ext import commands
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation

# Admin IDs
admin_ids = [1234567890]

class AdminStatCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, user_id):
        return user_id in admin_ids

    @commands.command(name='admin:stat', aliases=['a:stat'])
    async def admin_stat(self, ctx, user_id: str):
        if not self.is_admin(ctx.author.id):
            await ctx.send("You are not authorized to use this command.")
            return
        try:
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
            if not user:
                await ctx.send(f"No user found with ID: {user_id}.")
                return
        except DatabaseError:
            await ctx.send(content="Database Error! Contact Bot admins!")
            return

        user_lang = user.get("lang", "CHS")

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


        in_game_username = user.get("in_game_username", "Unknown")
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
    await bot.add_cog(AdminStatCommand(bot))
