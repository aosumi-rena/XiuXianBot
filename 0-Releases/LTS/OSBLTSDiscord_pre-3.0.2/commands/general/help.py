import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from utils.localisations import get_response
from utils.database import get_collection

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Displays the help message and command list.")
    async def help_command(self, interaction: discord.Interaction):
        """Displays the help message and command list (slash version)."""
        try:
            user_id = str(interaction.user.id)
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"

            response_type, xx_commands = get_response(
                'xx_commands',
                xx_version=self.bot.version,
                lang=user_lang
            )

            tos_button = Button(
                label="服务条款 | ToS",
                url="https://www.google.com/error"
            )
            privacy_button = Button(
                label="隐私政策 | Privacy",
                url="https://www.google.com/error"
            )
            add_bot_button = Button(
                label="添加Bot | Add Bot",
                url="https://www.google.com/error"
            )
            vote_button = Button(
                label="💎Vote",
                url="https://www.google.com/error"
            )

            view = View()
            view.add_item(tos_button)
            view.add_item(privacy_button)
            view.add_item(add_bot_button)
            view.add_item(vote_button)

            embed = discord.Embed(
                title="Cultivation - Help",
                description=xx_commands,
                color=0x00f2ff
            )

            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            print(f"Error in help_command (slash): {e}")
            await interaction.response.send_message(
                "出现错误，请稍后再试！\nERROR, try again later",
                ephemeral=True
            )

    @commands.command(name="help", aliases=["h","bz"])
    async def help_command_prefix(self, ctx: commands.Context):
        try:
            user_id = str(ctx.author.id)
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"

            response_type, xx_commands = get_response(
                'xx_commands',
                xx_version=self.bot.version,
                lang=user_lang
            )

            tos_button = Button(
                label="服务条款 | ToS",
                url="https://www.google.com/error"
            )
            privacy_button = Button(
                label="隐私政策 | Privacy",
                url="https://www.google.com/error"
            )
            add_bot_button = Button(
                label="添加Bot | Add Bot",
                url="https://www.google.com/error"
            )
            vote_button = Button(
                label="💎Vote",
                url="https://www.google.com/error"
            )

            view = View()
            view.add_item(tos_button)
            view.add_item(privacy_button)
            view.add_item(add_bot_button)
            view.add_item(vote_button)

            embed = discord.Embed(
                title="Cultivation - Help",
                description=xx_commands,
                color=0x00f2ff
            )

            await ctx.send(embed=embed, view=view)
        except Exception as e:
            print(f"Error in help_command (prefix): {e}")
            await ctx.send("出现错误，请稍后再试！\nERROR, try again later")

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
