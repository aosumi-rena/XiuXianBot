import discord
from discord.ext import commands
from utils.localisations import get_response
from utils.database import get_collection, DatabaseError

class TestCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='test', aliases=['cs', 'beta'])
    async def test(self, ctx):
        """Command to view the test details for this cycle."""
        try:
            user_id = str(ctx.author.id)
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"
        except DatabaseError:
            await ctx.send(content="Database Error! Contact Bot admins!")

        response_type, text = get_response('test_rewards', version=self.bot.version, lang=user_lang)

        if response_type == "embed":
            embed = discord.Embed(title="Test Details", description=text, color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            await ctx.send(text)

async def setup(bot):
    await bot.add_cog(TestCommand(bot))
