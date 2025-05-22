# Add your contact details for users to contact
import discord
from discord.ext import commands

class ContactCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="contact", aliases=["cont", "contacts", "lx"])
    async def contact(self, ctx):
        """Displays contact information."""
        embed = discord.Embed(
            title="Contact Information | 联系信息",
            description=("""
## Bug Report | Bug报告:
1. **Discord (Recommended for quick fix)**: ```<Discord_Username>```
2. **[Github](<https://github.com/aosumi-rena/XiuXianBot/issues>)**
## Other Feedbacks | 其他建议
1. **Email**: something@something.com
            """),
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ContactCommand(bot))
