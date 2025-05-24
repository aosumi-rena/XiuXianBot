from discord.ext import commands
from utils.localisations import get_response

class VersionCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ver', aliases=['version'])
    async def ver(self, ctx):
        """Check the Bot version."""
        response_type, text = get_response('version_info', version=self.bot.version, lang="EN")
        await ctx.reply(text)

async def setup(bot):
    await bot.add_cog(VersionCommand(bot))