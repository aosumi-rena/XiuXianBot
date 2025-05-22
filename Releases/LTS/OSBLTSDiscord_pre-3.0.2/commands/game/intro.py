import discord
from discord.ext import commands
from utils.localisations import get_response
from utils.database import get_collection


class IntroCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='intro', aliases=['js', 'introduction'])
    async def intro(self, ctx):
        """Command for Bot introductions."""
        user_id = str(ctx.author.id)
        user_collection = get_collection('users')
        user = user_collection.find_one({"user_id": user_id})
        user_lang = user.get("lang", "CHS") if user else "CHS"

        response_type, text = get_response('intro_text', lang=user_lang)

        if response_type == "embed":
            embed = discord.Embed(title="Introductions", description=text, color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            await ctx.send(text)

async def setup(bot):
    await bot.add_cog(IntroCommand(bot))
