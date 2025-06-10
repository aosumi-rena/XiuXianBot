import os
import sys
import logging
import aiohttp

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import json

import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button

from core.utils.localisation import get_response, load_localisation
from core.utils.account_status import format_status_text

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "logs")
LOG_DIR = os.path.abspath(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "discord.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("discord")

DEFAULT_SERVER_PORT = 11450
SERVER_URL = f"http://127.0.0.1:{DEFAULT_SERVER_PORT}"
intents = discord.Intents.default()
intents.message_content = True


class AccountModal(Modal):
    def __init__(self, user_id: str):
        super().__init__(title="账号创建 | Create Account")
        self.user_id = user_id
        self.add_item(TextInput(label="游戏用户名 - Username", placeholder="Your name"))
        self.add_item(TextInput(label="语言 - Lang (EN/CHS)", placeholder="CHS"))

    async def on_submit(self, interaction: discord.Interaction):
        username = self.children[0].value.strip()
        lang = self.children[1].value.strip().upper() or "CHS"
        payload = {
            "platform": "discord",
            "platform_id": self.user_id,
            "username": username,
            "lang": lang,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{SERVER_URL}/api/register", json=payload, timeout=10) as r:
                    data = await r.json()
            if r.status == 200 and data.get("success"):
                await interaction.response.send_message(
                    f"✅ UID: {data['user_id']}", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ {data.get('message', 'error')}", ephemeral=True
                )
        except Exception as exc:
            logger.error(f"register error: {exc}")
            await interaction.response.send_message("Server error", ephemeral=True)
class RegisterCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="register", aliases=["start", "ks", "begin"])
    async def register(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{SERVER_URL}/api/user/lookup",
                    params={"platform": "discord", "platform_id": user_id},
                    timeout=10,
                ) as r:
                    data = await r.json()
            if r.status == 200 and data.get("success"):
                lang = data.get("lang", "CHS")
                username = data.get("username", ctx.author.name)
                _, text = get_response("already_account", user=username, lang=lang)
                await ctx.send(text)
                return
        except Exception as exc:
            logger.error(f"lookup error: {exc}")

        modal = AccountModal(user_id)
        view = View()
        view.add_item(Button(label="打开表单 (Open Form)", style=discord.ButtonStyle.primary, custom_id="open"))

        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("This button is not for you", ephemeral=True)
                return
            await interaction.response.send_modal(modal)

        view.children[0].callback = button_callback
        _, text = get_response("account_creation_prompt", lang="CHS")
        await ctx.send(text, view=view)


class StatusCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="stat", aliases=["status", "zt"])
    async def stat(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{SERVER_URL}/api/user/lookup",
                    params={"platform": "discord", "platform_id": user_id},
                    timeout=10,
                ) as r:
                    lookup_data = await r.json()
            if r.status != 200 or not lookup_data.get("success"):
                _, text = get_response("no_account", user=ctx.author.name, lang="CHS")
                await ctx.send(text)
                return
            uid = lookup_data["user_id"]
            lang = lookup_data.get("lang", "CHS")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{SERVER_URL}/api/stat/{uid}", timeout=10) as rs:
                    data = await rs.json()
            if rs.status == 200 and data.get("success"):
                status_info = data["status"]
                text = format_status_text(status_info, lang, platform="discord")
                await ctx.send(text)
                return
        except Exception as exc:
            logger.error(f"status error: {exc}")
        await ctx.send("Error fetching status")
class CultivateCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="cul", aliases=["cultivate", "xl", "sit"])
    async def cultivate(self, ctx: commands.Context, action: str = None):
        user_id = str(ctx.author.id)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{SERVER_URL}/api/user/lookup",
                    params={"platform": "discord", "platform_id": user_id},
                    timeout=10,
                ) as lookup:
                    lookup_data = await lookup.json()
            if lookup.status != 200 or not lookup_data.get("success"):
                _, text = get_response("no_account", user=ctx.author.name, lang="CHS")
                await ctx.send(text)
                return
            uid = lookup_data["user_id"]
            lang = lookup_data.get("lang", "CHS")
            username = lookup_data.get("username", ctx.author.name)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{SERVER_URL}/api/cultivate/status/{uid}", timeout=10) as r:
                    status = await r.json()
            cultivating = status.get("state", False)

            if action == "stat":
                if not cultivating:
                    await ctx.send("未在修炼 | Not cultivating")
                else:
                    current = status.get("current_gain")
                    await ctx.send(f"修炼中，已获得 {current} 修为")
                return

            if (action == "start" or action is None) and not cultivating:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{SERVER_URL}/api/cultivate/start", json={"user_id": uid}, timeout=10) as r:
                        data = await r.json()
                if r.status == 200 and data.get("success"):
                    _, text = get_response(
                        "cultivation_start",
                        user=username,
                        lang=lang,
                    )
                    await ctx.send(text)
                else:
                    await ctx.send(data.get("message", "Error"))
                return

            if (action == "end" or action is None) and cultivating:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{SERVER_URL}/api/cultivate/end", json={"user_id": uid}, timeout=10) as r:
                        data = await r.json()
                if r.status == 200 and data.get("success"):
                    _, text = get_response(
                        "cultivation_end",
                        culti_gain=data["gain"],
                        lang=lang,
                    )
                    await ctx.send(text)
                else:
                    await ctx.send(data.get("message", "Error"))
                return

            await ctx.send("❌ 无效操作 | Invalid action")
        except Exception as exc:
            logger.error(f"cultivate error: {exc}")
            await ctx.send("Server error")


class XiuXianBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="^", intents=intents, help_command=None)
        self.version = "OSRELDocker0.1.51-beta (Discord Adapter 0.1.0)"

    async def setup_hook(self):
        await self.add_cog(RegisterCommand(self))
        await self.add_cog(StatusCommand(self))
        await self.add_cog(CultivateCommand(self))


def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "config.json")
    config_path = os.path.abspath(config_path)
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error(f"Failed to load config: {exc}")
        return None


def main():
    config = load_config()
    if not config:
        return
    global SERVER_URL
    server_port = config.get("core_server", {}).get("port", DEFAULT_SERVER_PORT)
    SERVER_URL = f"http://127.0.0.1:{server_port}"
    token = config.get("tokens", {}).get("discord_token")
    bot = XiuXianBot()
    bot.run(token)


if __name__ == "__main__":
    main()
