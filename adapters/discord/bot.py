"""
Main file for discord adapter
"""

import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, Button, View
import asyncio
import logging
import os
import sys
import json
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.database import get_collection, DatabaseError
from core.utils.localisation import get_response, load_localisation

import os
log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'discord.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.dm_messages = True

class XiuXianBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='^',
            intents=intents,
            help_command=None
        )
        self.version = "4.0.0-dev"
        
    async def setup_hook(self):
        logger.info("Setting up Discord bot...")
        
        await self.load_commands()
        
        logger.info("Discord bot setup complete")
    
    async def load_commands(self):
        try:
            await self.add_cog(StartCommand(self))
            await self.add_cog(StatusCommand(self))
            await self.add_cog(CultivateCommand(self))
            await self.add_cog(HelpCommand(self))
            await self.add_cog(AccountCommand(self))
            await self.add_cog(HuntCommand(self))
            await self.add_cog(AscendCommand(self))
            await self.add_cog(DailyCommand(self))
            await self.add_cog(ShopCommand(self))
            await self.add_cog(InventoryCommand(self))
            await self.add_cog(ElementCommand(self))
            await self.add_cog(LunarCommand(self))
            await self.add_cog(VersionCommand(self))
            
            logger.info("All command cogs loaded successfully")
        except Exception as e:
            logger.error(f"Error loading command cogs: {e}")
    
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        await self.change_presence(
            activity=discord.Game(name="修仙 | ^help for commands")
        )
    
    async def on_message(self, message):
        if message.author.bot:
            return
        
        await self.handle_raw_commands(message)
        
        await self.process_commands(message)
    
    async def handle_raw_commands(self, message):
        content = message.content.strip()
        
        raw_commands = {
            "开始": "start",
            "注册": "start",
            "状态": "stat",
            "测试": "test",
            "介绍": "intro",
            "修炼": "cultivate",
            "修仙": "cultivate",
            "打坐": "cultivate",
            "闭关": "cultivate",
            "突破": "ascend",
            "渡劫": "ascend",
            "升阶": "ascend",
            "签到": "daily",
            "每日": "daily",
            "打野": "hunt",
            "打猎": "hunt",
            "狩猎": "hunt",
            "版本": "version",
            "版本信息": "version",
            "物品": "inventory",
            "物品栏": "inventory",
            "背包": "inventory",
            "帮助": "help",
            "命令": "help",
            "指令": "help",
            "商店": "shop",
            "元素": "element",
            "五行": "element",
            "属性": "element",
            "黄历": "lunar",
            "运势": "lunar",
            "账号": "account",
            "联系": "contact"
        }
        
        if content in raw_commands:
            ctx = await self.get_context(message)
            command_name = raw_commands[content]
            command = self.get_command(command_name)
            if command:
                await ctx.invoke(command)
            else:
                if command_name in ["test", "intro", "contact"]:
                    await ctx.send("🚧 功能开发中 | Feature under development")

class AccountCreationModal(Modal):
    def __init__(self, user_id, username, user_collection):
        super().__init__(title="账号创建 | Creating Account")
        self.user_id = user_id
        self.username = username
        self.user_collection = user_collection
        
        self.add_item(TextInput(
            label="游戏用户名 - Enter Username", 
            placeholder="你的游戏名 | Your Username", 
            style=discord.TextStyle.short
        ))
        self.add_item(TextInput(
            label="选择语言 - Choose Lang (EN/CHS/CHT)", 
            placeholder="EN/CHS/CHT", 
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if interaction.response.is_done():
                logger.warning(f"Interaction already responded to for Discord user {self.user_id}")
                return
                
            logger.info(f"Account creation modal submitted by Discord user {self.user_id} ({self.username})")
            
            in_game_username = self.children[0].value.strip()
            new_language = self.children[1].value.strip().upper()

            if len(in_game_username) > 40:
                await interaction.response.send_message(
                    "Username cannot exceed 40 characters! 用户名不能超过40个字符！", 
                    ephemeral=True
                )
                logger.info(f"Account creation failed for {self.user_id}: username too long")
                return

            if new_language not in ["EN", "CHS", "CHT"]:
                await interaction.response.send_message(
                    "语言无效，请输入(Invalid language format, enter one of the following): EN | CHS | CHT", 
                    ephemeral=True
                )
                logger.info(f"Account creation failed for {self.user_id}: invalid language {new_language}")
                return

            from core.utils.database import generate_universal_uid
            universal_uid = generate_universal_uid()
            if not universal_uid:
                logger.error(f"Failed to generate universal UID for Discord user {self.user_id}")
                await interaction.response.send_message(
                    "创建账号时出错，请联系管理员。\n"
                    "Error creating account, please contact admins.",
                    ephemeral=True
                )
                return
                
            user_data = {
                "user_id": universal_uid,
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
                "third_party_ids": {
                    "discord": self.user_id,
                    "telegram": "",
                    "matrix": ""
                }
            }
            
            try:
                self.user_collection.insert_one(user_data)
                logger.info(f"Successfully created account for Discord user {self.user_id} with UID {universal_uid}")
                await interaction.response.send_message(
                    f"账号创建成功！欢迎 {in_game_username}，语言已设置为 {new_language}。\n"
                    f"Account created! Welcome {in_game_username}, your language has been set to {new_language} in following messages.\n"
                    f"您的通用 UID: {universal_uid} | Your Universal UID: {universal_uid}",
                    ephemeral=True
                )
            except Exception as e:
                logger.error(f"Database error creating account for Discord user {self.user_id}: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "创建账号时出错，请联系管理员。\nError creating account, please contact admins.",
                        ephemeral=True
                    )
                    
        except discord.errors.InteractionResponded:
            logger.warning(f"Interaction already responded to in modal submission for Discord user {self.user_id}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout error in modal submission for Discord user {self.user_id}")
        except Exception as e:
            logger.error(f"Unhandled error in modal submission for Discord user {self.user_id}: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "处理请求时出错，请稍后再试。\nError processing request, please try again later.",
                        ephemeral=True
                    )
            except Exception as inner_e:
                logger.error(f"Failed to send error response for Discord user {self.user_id}: {inner_e}")

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

class StatusCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='stat', aliases=['zt', 'status'])
    async def stat(self, ctx):
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

        try:
            from core.utils.account_status import get_user_status
            status_info = get_user_status(user_id, user_lang)
            
            if status_info:
                progress = status_info['progress_percentage']
                progress_bar_length = 10
                filled_length = int(progress_bar_length * progress / 100)
                progress_bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
                
                embed = discord.Embed(
                    title=f"修仙状态 | Cultivation Status",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="道号 | Username",
                    value=f"**{status_info['in_game_username']}**",
                    inline=True
                )
                
                embed.add_field(
                    name="UID",
                    value=f"`{status_info['user_id']}`",
                    inline=True
                )
                
                embed.add_field(
                    name="境界 | Stage",
                    value=f"{status_info['stage_description']} (第{status_info['rank']}重)",
                    inline=True
                )
                
                embed.add_field(
                    name="修为 | Cultivation",
                    value=f"{status_info['exp']:,}/{status_info['max_exp']:,}\n{progress_bar} {progress:.1f}%",
                    inline=True
                )
                
                embed.add_field(
                    name="元素 | Element",
                    value=status_info['element'],
                    inline=True
                )
                
                embed.add_field(
                    name="资源 | Resources",
                    value=f"💰 铜币: {status_info['copper']:,}\n💎 元宝: {status_info['gold']:,}",
                    inline=True
                )
                
                embed.add_field(
                    name="状态 | State",
                    value=f"🧘 {'修炼中' if status_info['state'] else '空闲'}\n📅 每日次数: {status_info['dy_times']}/3",
                    inline=True
                )
                
                await ctx.send(embed=embed)
            else:
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
        except ImportError:
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

class CultivateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cul', aliases=['xl', 'sit'])
    async def cultivate(self, ctx):
        try:
            user_id = str(ctx.author.id)
            user_collection = get_collection('users')
            timing_collection = get_collection('timings')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"
        except DatabaseError:
            await ctx.send("Database Error! Contact Bot admins!")
            return

        if not user:
            rtype, text = get_response('no_account', user=ctx.author.mention, lang=user_lang)
            await ctx.send(text)
            return

        if user.get('state', False):
            rtype, text = get_response('train_in_progress', user=user['in_game_username'], lang=user_lang)
            await ctx.send(text)
            return

        import random
        import datetime
        
        base_culti_gain = random.randint(150, 250)
        actual_culti_gain = base_culti_gain 
        
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(hours=2)
        user_collection.update_one({"user_id": user_id}, {"$set": {"state": True}})

        timing_collection.insert_one({
            "user_id": user_id,
            "start_time": int(start_time.timestamp()),
            "end_time": int(end_time.timestamp()),
            "type": "cultivation",
            "culti_gain": actual_culti_gain
        })

        rtype, text = get_response(
            'cultivation_start',
            user=user['in_game_username'],
            end_time=f"<t:{int(end_time.timestamp())}:R>",
            culti_gain=actual_culti_gain,
            lang=user_lang
        )
        await ctx.send(text)

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

            embed = discord.Embed(
                title="Cultivation - Help",
                description=xx_commands,
                color=0x00f2ff
            )

            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in help_command (prefix): {e}")
            await ctx.send("出现错误，请稍后再试！\nERROR, try again later")

class AccountCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='acc', aliases=['account'])
    async def account(self, ctx):
        try:
            user_id = str(ctx.author.id)
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"
        except DatabaseError:
            await ctx.send("Database Error! Contact Bot admins!")
            return

        if not user:
            response_type, text = get_response('no_account', user=ctx.author.mention, lang=user_lang)
            await ctx.send(text)
            return

        embed = discord.Embed(
            title="账号管理 | Account Management",
            color=0x00ff00
        )
        
        embed.add_field(
            name="用户信息 | User Info",
            value=f"**用户名 | Username:** {user.get('in_game_username', 'N/A')}\n"
                  f"**UID:** `{user_id}`\n"
                  f"**语言 | Language:** {user.get('lang', 'CHS')}",
            inline=False
        )
        
        third_party_ids = user.get('third_party_ids', {})
        platform_info = []
        
        for platform, platform_id in third_party_ids.items():
            if platform_id and platform_id.strip():
                platform_info.append(f"✅ {platform.title()}: `{platform_id}`")
            else:
                platform_info.append(f"❌ {platform.title()}: 未关联 | Not linked")
        
        embed.add_field(
            name="平台关联 | Platform Links",
            value="\n".join(platform_info) if platform_info else "无关联平台 | No linked platforms",
            inline=False
        )
        
        embed.add_field(
            name="可用命令 | Available Commands",
            value="• `^link <UID> [platform]` - 关联账号 | Link account\n"
                  "• `^unlink <platform>` - 取消关联 | Unlink account",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='link')
    async def link_account(self, ctx, universal_uid: str = None):
        if not universal_uid:
            await ctx.send(
                "使用方法 | Usage: `^link <Universal UID>`\n"
                "例如 | Example: `^link 1000001`\n"
                "这将把您的 Discord 账号关联到指定的通用 UID\n"
                "This will link your Discord account to the specified Universal UID"
            )
            return
        
        discord_user_id = str(ctx.author.id)
        
        try:
            import requests
            user_collection = get_collection('users')
            
            target_user = user_collection.find_one({"user_id": universal_uid})
            if not target_user:
                logger.error(f"Link attempt failed: Universal UID {universal_uid} not found")
                await ctx.send("❌ 未找到指定的 Universal UID | Universal UID not found")
                return
            
            existing_user = user_collection.find_one({"third_party_ids.discord": discord_user_id})
            if existing_user:
                logger.error(f"Link attempt failed: Discord user {discord_user_id} already linked to UID {existing_user.get('user_id')}")
                await ctx.send(
                    f"❌ 您的 Discord 账号已关联到 UID: {existing_user.get('user_id')}\n"
                    f"Your Discord account is already linked to UID: {existing_user.get('user_id')}\n"
                    f"请先使用 `^unlink discord` 解除关联 | Please use `^unlink discord` first to unlink"
                )
                return
            
            if target_user.get('third_party_ids', {}).get('discord'):
                logger.error(f"Link attempt failed: UID {universal_uid} already has Discord linked")
                await ctx.send(
                    f"❌ 该 UID 已关联其他 Discord 账号\n"
                    f"This UID is already linked to another Discord account"
                )
                return
            
            response = requests.post('http://localhost:11451/api/link-account', json={
                'user_id': universal_uid,
                'platform': 'discord',
                'platform_id': discord_user_id
            }, timeout=10)
            
            if response.status_code == 200 and response.json().get('success'):
                logger.info(f"Successfully linked Discord user {discord_user_id} to UID {universal_uid}")
                await ctx.send(
                    f"✅ 账号关联成功！| Account linked successfully!\n"
                    f"您的 Discord 账号已关联到 UID: {universal_uid}\n"
                    f"Your Discord account has been linked to UID: {universal_uid}"
                )
            else:
                error_msg = response.json().get('message', 'Unknown error')
                logger.error(f"API error linking account: {error_msg}")
                await ctx.send(
                    f"❌ 关联过程中出现错误: {error_msg}\n"
                    f"Error during linking process: {error_msg}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during account linking: {e}")
            await ctx.send(
                "❌ 网络连接错误，请稍后重试\n"
                "Network connection error, please try again later"
            )
        except Exception as e:
            logger.error(f"Unexpected error in link command: {e}")
            await ctx.send("❌ 关联过程中出现错误 | Error during linking process")

    @commands.command(name='verify')
    async def verify_otp(self, ctx, otp_code: str = None):
        await ctx.send(
            "验证功能暂未实现，请使用 `^link <UID>` 直接关联账号\n"
            "Verify function not implemented, please use `^link <UID>` to link account directly"
        )

    @commands.command(name='unlink')
    async def unlink_account(self, ctx, platform: str = None):
        if not platform or platform.lower() not in ['discord', 'telegram', 'matrix']:
            await ctx.send(
                "使用方法 | Usage: `^unlink <platform>`\n"
                "平台选项 | Platform options: discord, telegram, matrix"
            )
            return
        
        discord_user_id = str(ctx.author.id)
        platform = platform.lower()
        
        try:
            import requests
            user_collection = get_collection('users')
            
            user = user_collection.find_one({"third_party_ids.discord": discord_user_id})
            if not user:
                await ctx.send("❌ 未找到您的账号 | Your account not found")
                return
            
            user_id = user.get('user_id')
            
            response = requests.post('http://localhost:11451/api/unlink-account', json={
                'user_id': user_id,
                'platform': platform
            }, timeout=10)
            
            if response.status_code == 200 and response.json().get('success'):
                logger.info(f"Successfully unlinked {platform} from UID {user_id}")
                await ctx.send(f"✅ 已取消 {platform.title()} 平台关联 | {platform.title()} account unlinked successfully")
            else:
                error_msg = response.json().get('message', 'Unknown error')
                logger.error(f"API error unlinking account: {error_msg}")
                await ctx.send(f"❌ 取消关联失败: {error_msg} | Failed to unlink {platform} account: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during account unlinking: {e}")
            await ctx.send(
                "❌ 网络连接错误，请稍后重试\n"
                "Network connection error, please try again later"
            )
        except Exception as e:
            logger.error(f"Unexpected error in unlink command: {e}")
            await ctx.send("❌ 取消关联过程中出现错误 | Error during unlinking")

class HuntCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hunt', aliases=['dy'])
    async def hunt(self, ctx):
        await ctx.send("Hunt feature - Coming soon!")

class AscendCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='asc', aliases=['ascend'])
    async def ascend(self, ctx):
        await ctx.send("Ascend feature - Coming soon!")

class DailyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='daily', aliases=['sign'])
    async def daily(self, ctx):
        await ctx.send("Daily sign-in - Coming soon!")

class ShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='shop')
    async def shop(self, ctx):
        await ctx.send("Shop feature - Coming soon!")

class InventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='inv', aliases=['inventory'])
    async def inventory(self, ctx):
        await ctx.send("Inventory feature - Coming soon!")

class ElementCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ele', aliases=['element'])
    async def element(self, ctx):
        await ctx.send("Element feature - Coming soon!")

class LunarCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lunar')
    async def lunar(self, ctx):
        await ctx.send("Lunar calendar - Coming soon!")

class VersionCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ver', aliases=['version'])
    async def version(self, ctx):
        await ctx.send(f"XiuXianBot Discord Adapter v{self.bot.version}")

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.normpath(os.path.join(script_dir, os.pardir, os.pardir, "config.json"))

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"config.json not found at {config_path!r}")
        return None

def main():
    config = load_config()
    if not config:
        logger.error("Failed to load configuration")
        return

    from core.utils.database import connect_mongo
    connect_mongo()

    token = config.get('tokens', {}).get('discord_token')
    if not token:
        logger.error("Discord token not found in config")
        return

    bot = XiuXianBot()
    
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"Error running Discord bot: {e}")

if __name__ == "__main__":
    main()
