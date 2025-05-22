import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, Button, View
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response


class AccountCreationModal(Modal):
    def __init__(self, user_id, username, user_collection):
        super().__init__(title="账号创建 | Creating Account")
        self.user_id = user_id
        self.username = username
        self.user_collection = user_collection
        self.add_item(TextInput(label="游戏用户名 - Enter Username", placeholder="你的游戏名 | Your Username", style=discord.TextStyle.short))
        self.add_item(TextInput(label="选择语言 - Choose Lang (EN/CHS/CHT)", placeholder="EN/CHS/CHT", style=discord.TextStyle.short))

    async def on_submit(self, interaction: discord.Interaction):
        in_game_username = self.children[0].value.strip()
        new_language = self.children[1].value.strip().upper()

        if len(in_game_username) > 40:
            await interaction.response.send_message("Username cannot exceed 40 characters! 用户名不能超过40个字符！", ephemeral=True)
            return

        if new_language not in ["EN", "CHS", "CHT"]:
            await interaction.response.send_message("语言无效，请输入(Invalid language format, enter one of the following): EN | CHS | CHT", ephemeral=True)
            return

        user_data = {
            "user_id": self.user_id,
            "discord_username": self.username,
            "in_game_username": in_game_username,
            "lang": new_language,
            "state": False,
            "exp": 0,
            "rank": 1,
            "dy_times": 0,
            "copper": 0,
            "gold": 0,
            "asc_reduction": 0,
            "sign": False,
        }
        self.user_collection.insert_one(user_data)

        await interaction.response.send_message(
            f"账号创建成功！欢迎 {in_game_username}，语言已设置为 {new_language}。\nAccount created! Welcome {in_game_username}, your language has been set to {new_language} in following messages.",
            ephemeral=True
        )


class AccountCreationView(View):
    def __init__(self, modal):
        super().__init__()
        self.modal = modal

    @discord.ui.button(label="打开表单 (Open Form)", style=discord.ButtonStyle.primary)
    async def open_form(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(self.modal)


class StartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='start', aliases=['ks', 'begin'])
    async def start(self, ctx):
        """Command to create an account."""
        try:
            user_id = str(ctx.author.id)
            username = ctx.author.name
            user_collection = get_collection('users')
        except DatabaseError:
            await ctx.send(content="Database Error! Contact Bot admins!")
            return

        user = user_collection.find_one({"user_id": user_id})
        user_lang = user.get("lang", "CHS") if user else "CHS"

        if user:
            in_game_username = user.get("in_game_username", ctx.author.mention)
            response_type, text = get_response('already_account', user=in_game_username, lang=user_lang)
            await ctx.send(text, ephemeral=True)
            return

        modal = AccountCreationModal(user_id, username, user_collection)
        view = AccountCreationView(modal)
        response_type, text = get_response('account_creation_prompt', lang=user_lang)
        await ctx.send(text, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(StartCommand(bot))
