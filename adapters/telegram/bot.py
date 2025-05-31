"""
Main file for telegram adapter
"""

import asyncio
import logging
import os
import sys
import json
import requests
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

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
        logging.FileHandler(os.path.join(log_dir, 'telegram.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('telegram')

class XiuXianTelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.version = "4.0.0-dev"
        
    async def setup_commands(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("register", self.register_command))
        self.application.add_handler(CommandHandler("link", self.link_command))
        self.application.add_handler(CommandHandler("stat", self.stat_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_raw_commands))
        
        commands = [
            BotCommand("start", "开始使用机器人 | Start using the bot"),
            BotCommand("register", "注册新账号 | Register new account"),
            BotCommand("link", "关联账号 | Link account"),
            BotCommand("verify", "验证OTP | Verify OTP"),
            BotCommand("unlink", "取消关联 | Unlink account"),
            BotCommand("stat", "查看状态 | Check status"),
            BotCommand("help", "获取帮助 | Get help")
        ]
        
        await self.application.bot.set_my_commands(commands)
        logger.info("Telegram bot commands set up successfully")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or update.effective_user.first_name
        
        try:
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"
        except DatabaseError:
            await update.message.reply_text("Database Error! Contact Bot admins!")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("帮助 | Help", callback_data="help"),
                InlineKeyboardButton("账号 | Account", callback_data="account")
            ],
            [
                InlineKeyboardButton("注册新账号 | Register", callback_data="register"),
                InlineKeyboardButton("关联账号 | Link", callback_data="link")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "🌟 欢迎来到修仙世界！Welcome to XiuXian World! 🌟\n\n"
            "这是一个文字修仙游戏机器人。\n"
            "This is a text-based cultivation game bot.\n\n"
            "📋 使用前请阅读服务条款和隐私政策：\n"
            "Please read our Terms of Service and Privacy Policy before use:\n"
            "• 本机器人仅供娱乐使用\n"
            "• 请勿分享个人敏感信息\n"
            "• 游戏数据可能会被重置\n\n"
            "选择下方按钮开始：\nChoose an option below to start:"
        )
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or update.effective_user.first_name
        
        try:
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"
        except DatabaseError:
            await update.message.reply_text("Database Error! Contact Bot admins!")
            return
        
        if user:
            in_game_username = user.get("in_game_username", username)
            response_type, text = get_response('already_account', user=in_game_username, lang=user_lang)
            await update.message.reply_text(text)
            return
        
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "使用方法 | Usage: /register <用户名|username> <语言|language>\n"
                "例如 | Example: /register 张三 CHS\n"
                "语言选项 | Language options: EN, CHS, CHT"
            )
            return
        
        in_game_username = args[0].strip()
        new_language = args[1].strip().upper()
        
        if len(in_game_username) > 40:
            await update.message.reply_text(
                "用户名不能超过40个字符！\nUsername cannot exceed 40 characters!"
            )
            return
        
        if new_language not in ["EN", "CHS", "CHT"]:
            await update.message.reply_text(
                "语言无效，请输入: EN | CHS | CHT\n"
                "Invalid language, please enter: EN | CHS | CHT"
            )
            return
        
        from core.utils.database import generate_universal_uid
        universal_uid = generate_universal_uid()
        if not universal_uid:
            await update.message.reply_text(
                "创建账号时出错，请联系管理员。\n"
                "Error creating account, please contact admins."
            )
            return
            
        user_data = {
            "user_id": universal_uid,
            "telegram_username": username,
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
                "discord": "",
                "telegram": user_id,
                "matrix": ""
            }
        }
        
        try:
            user_collection.insert_one(user_data)
            await update.message.reply_text(
                f"✅ 账号创建成功！欢迎 {in_game_username}，语言已设置为 {new_language}。\n"
                f"Account created! Welcome {in_game_username}, your language has been set to {new_language}."
            )
        except Exception as e:
            logger.error(f"Error creating account: {e}")
            await update.message.reply_text(
                "创建账号时出错，请联系管理员。\n"
                "Error creating account, please contact admins."
            )
    
    async def link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 1:
            await update.message.reply_text(
                "使用方法 | Usage: /link <Universal UID>\n"
                "例如 | Example: /link 1000001\n"
                "这将把您的 Telegram 账号关联到指定的通用 UID\n"
                "This will link your Telegram account to the specified Universal UID"
            )
            return
        
        universal_uid = args[0].strip()
        telegram_user_id = str(update.effective_user.id)
        
        try:
            import requests
            user_collection = get_collection('users')
            
            target_user = user_collection.find_one({"user_id": universal_uid})
            if not target_user:
                logger.error(f"Link attempt failed: Universal UID {universal_uid} not found")
                await update.message.reply_text("❌ 未找到指定的 Universal UID | Universal UID not found")
                return
            
            existing_user = user_collection.find_one({"third_party_ids.telegram": telegram_user_id})
            if existing_user:
                logger.error(f"Link attempt failed: Telegram user {telegram_user_id} already linked to UID {existing_user.get('user_id')}")
                await update.message.reply_text(
                    f"❌ 您的 Telegram 账号已关联到 UID: {existing_user.get('user_id')}\n"
                    f"Your Telegram account is already linked to UID: {existing_user.get('user_id')}\n"
                    f"请先使用 /unlink 解除关联 | Please use /unlink first to unlink"
                )
                return
            
            if target_user.get('third_party_ids', {}).get('telegram'):
                logger.error(f"Link attempt failed: UID {universal_uid} already has Telegram linked")
                await update.message.reply_text(
                    f"❌ 该 UID 已关联其他 Telegram 账号\n"
                    f"This UID is already linked to another Telegram account"
                )
                return
            
            response = requests.post('http://localhost:11451/api/link-account', json={
                'user_id': universal_uid,
                'platform': 'telegram',
                'platform_id': telegram_user_id
            }, timeout=10)
            
            if response.status_code == 200 and response.json().get('success'):
                logger.info(f"Successfully linked Telegram user {telegram_user_id} to UID {universal_uid}")
                await update.message.reply_text(
                    f"✅ 账号关联成功！| Account linked successfully!\n"
                    f"您的 Telegram 账号已关联到 UID: {universal_uid}\n"
                    f"Your Telegram account has been linked to UID: {universal_uid}"
                )
            else:
                error_msg = response.json().get('message', 'Unknown error')
                logger.error(f"API error linking account: {error_msg}")
                await update.message.reply_text(
                    f"❌ 关联过程中出现错误: {error_msg}\n"
                    f"Error during linking process: {error_msg}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during account linking: {e}")
            await update.message.reply_text(
                "❌ 网络连接错误，请稍后重试\n"
                "Network connection error, please try again later"
            )
        except Exception as e:
            logger.error(f"Unexpected error in link command: {e}")
            await update.message.reply_text("❌ 关联过程中出现错误 | Error during linking process")
    
    async def stat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        
        try:
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"
        except DatabaseError:
            await update.message.reply_text("Database Error! Contact Bot admins!")
            return
        
        if not user:
            response_type, text = get_response('no_account', user=update.effective_user.mention_markdown_v2(), lang=user_lang)
            await update.message.reply_text(text, parse_mode='MarkdownV2')
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
        
        in_game_username = user.get("in_game_username", update.effective_user.first_name)
        stage_description = load_localisation(user_lang)['xx_stage_descriptions'].get(str(user['rank']), "ERROR")
        max_exp = load_localisation(user_lang)['xx_stage_max'].get(str(user['rank']), "ERROR")
        
        try:
            from core.utils.account_status import get_user_status, format_status_text
            status_info = get_user_status(user_id, user_lang)
            
            if status_info:
                status_text = format_status_text(status_info, user_lang)
                await update.message.reply_text(status_text, parse_mode='Markdown')
            else:
                status_text = (
                    f"👤 **{in_game_username}**\n"
                    f"🆔 UID: `{user_id}`\n"
                    f"⭐ 境界: {stage_description}\n"
                    f"💫 修为: {user['exp']}/{max_exp}\n"
                    f"🔥 元素: {element}\n"
                    f"💰 铜币: {user['copper']}\n"
                    f"💎 元宝: {user['gold']}\n"
                    f"📅 每日次数: {user.get('dy_times', 0)}/3\n"
                    f"🧘 状态: {'修炼中' if user.get('state', False) else '空闲'}"
                )
                await update.message.reply_text(status_text, parse_mode='Markdown')
        except ImportError:
            status_text = (
                f"👤 **{in_game_username}**\n"
                f"🆔 UID: `{user_id}`\n"
                f"⭐ 境界: {stage_description}\n"
                f"💫 修为: {user['exp']}/{max_exp}\n"
                f"🔥 元素: {element}\n"
                f"💰 铜币: {user['copper']}\n"
                f"💎 元宝: {user['gold']}\n"
                f"📅 每日次数: {user.get('dy_times', 0)}/3\n"
                f"🧘 状态: {'修炼中' if user.get('state', False) else '空闲'}"
            )
            await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        
        try:
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
            user_lang = user.get("lang", "CHS") if user else "CHS"
        except DatabaseError:
            user_lang = "CHS"
        
        keyboard = [
            [
                InlineKeyboardButton("基础命令 | Basic", callback_data="help_basic"),
                InlineKeyboardButton("游戏命令 | Game", callback_data="help_game")
            ],
            [
                InlineKeyboardButton("账号管理 | Account", callback_data="help_account"),
                InlineKeyboardButton("返回主菜单 | Main", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        help_text = (
            f"📚 **修仙机器人帮助 | XiuXian Bot Help** v{self.version}\n\n"
            "🎮 **可用命令 | Available Commands:**\n"
            "• /start - 开始使用 | Start\n"
            "• /register - 注册账号 | Register\n"
            "• /link - 关联账号 | Link account\n"
            "• /stat - 查看状态 | Check status\n"
            "• /help - 获取帮助 | Get help\n\n"
            "🈶 **中文命令 | Chinese Commands:**\n"
            "你也可以直接发送中文命令，如：\n"
            "You can also send Chinese commands directly:\n"
            "• 状态 - 查看状态\n"
            "• 帮助 - 获取帮助\n"
            "• 注册 - 注册账号\n\n"
            "选择下方按钮获取详细帮助：\n"
            "Select a button below for detailed help:"
        )
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "help":
            await self.help_command(update, context)
        elif data == "account":
            await self.show_account_menu(query)
        elif data == "register":
            await query.edit_message_text(
                "📝 **注册新账号 | Register New Account**\n\n"
                "使用命令 | Use command:\n"
                "`/register <用户名> <语言>`\n\n"
                "例如 | Example:\n"
                "`/register 张三 CHS`\n\n"
                "语言选项 | Language options:\n"
                "• EN - English\n"
                "• CHS - 简体中文\n"
                "• CHT - 繁體中文",
                parse_mode='Markdown'
            )
        elif data == "link":
            await query.edit_message_text(
                "🔗 **关联账号 | Link Account**\n\n"
                "使用命令 | Use command:\n"
                "`/link <Universal UID> [platform]`\n\n"
                "例如 | Example:\n"
                "`/link 123456789 discord`\n\n"
                "平台选项 | Platform options:\n"
                "• discord\n"
                "• telegram\n"
                "• matrix",
                parse_mode='Markdown'
            )
        elif data == "help_basic":
            await self.show_basic_help(query)
        elif data == "help_game":
            await self.show_game_help(query)
        elif data == "help_account":
            await self.show_account_help(query)
        elif data == "main_menu":
            await self.show_main_menu(query)
    
    async def show_account_menu(self, query):
        keyboard = [
            [
                InlineKeyboardButton("查看状态 | Status", callback_data="check_status"),
                InlineKeyboardButton("账号设置 | Settings", callback_data="account_settings")
            ],
            [
                InlineKeyboardButton("关联账号 | Link", callback_data="link"),
                InlineKeyboardButton("返回主菜单 | Main", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👤 **账号管理 | Account Management**\n\n"
            "选择一个选项：\nChoose an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_basic_help(self, query):
        await query.edit_message_text(
            "📚 **基础命令帮助 | Basic Commands Help**\n\n"
            "🎯 **斜杠命令 | Slash Commands:**\n"
            "• `/start` - 显示主菜单\n"
            "• `/register <用户名> <语言>` - 注册新账号\n"
            "• `/link <UID> [平台]` - 关联账号\n"
            "• `/stat` - 查看状态\n"
            "• `/help` - 获取帮助\n\n"
            "🈶 **中文命令 | Chinese Commands:**\n"
            "• 帮助 - 获取帮助\n"
            "• 状态 - 查看状态\n"
            "• 注册 - 注册提示\n\n"
            "💡 **提示 | Tips:**\n"
            "你可以直接发送中文命令，无需前缀！\n"
            "You can send Chinese commands directly without prefix!",
            parse_mode='Markdown'
        )
    
    async def show_game_help(self, query):
        await query.edit_message_text(
            "🎮 **游戏命令帮助 | Game Commands Help**\n\n"
            "⚠️ **开发中 | Under Development**\n\n"
            "即将推出的功能 | Coming Soon:\n"
            "• 修仙/闭关 - 修炼功法\n"
            "• 打野/狩猎 - 获取资源\n"
            "• 突破/渡劫 - 提升境界\n"
            "• 签到/每日 - 每日奖励\n"
            "• 商店 - 购买物品\n"
            "• 背包 - 查看物品\n\n"
            "🔄 **当前版本只支持基础功能**\n"
            "Current version only supports basic features",
            parse_mode='Markdown'
        )
    
    async def show_account_help(self, query):
        await query.edit_message_text(
            "👤 **账号管理帮助 | Account Management Help**\n\n"
            "🔐 **账号关联 | Account Linking:**\n"
            "使用 Universal UID 关联多平台账号\n"
            "Link multi-platform accounts using Universal UID\n\n"
            "📱 **支持平台 | Supported Platforms:**\n"
            "• Discord\n"
            "• Telegram\n"
            "• Matrix (即将推出 | Coming Soon)\n\n"
            "🔒 **安全提示 | Security Tips:**\n"
            "• 不要分享你的 UID\n"
            "• 定期检查账号状态\n"
            "• 如有异常请联系管理员",
            parse_mode='Markdown'
        )
    
    async def show_main_menu(self, query):
        keyboard = [
            [
                InlineKeyboardButton("帮助 | Help", callback_data="help"),
                InlineKeyboardButton("账号 | Account", callback_data="account")
            ],
            [
                InlineKeyboardButton("注册新账号 | Register", callback_data="register"),
                InlineKeyboardButton("关联账号 | Link", callback_data="link")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🌟 **修仙世界主菜单 | XiuXian World Main Menu** 🌟\n\n"
            "选择下方按钮开始：\nChoose an option below to start:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_raw_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        content = update.message.text.strip()
        
        raw_commands = {
            "开始": self.start_command,
            "注册": self.show_register_help,
            "状态": self.stat_command,
            "我的状态": self.stat_command,
            "测试": self.coming_soon,
            "介绍": self.coming_soon,
            "修炼": self.coming_soon,
            "修仙": self.coming_soon,
            "打坐": self.coming_soon,
            "闭关": self.coming_soon,
            "突破": self.coming_soon,
            "渡劫": self.coming_soon,
            "升阶": self.coming_soon,
            "签到": self.coming_soon,
            "每日": self.coming_soon,
            "打野": self.coming_soon,
            "打猎": self.coming_soon,
            "狩猎": self.coming_soon,
            "版本": self.version_command,
            "版本信息": self.version_command,
            "物品": self.coming_soon,
            "物品栏": self.coming_soon,
            "背包": self.coming_soon,
            "帮助": self.help_command,
            "命令": self.help_command,
            "指令": self.help_command,
            "商店": self.coming_soon,
            "元素": self.coming_soon,
            "五行": self.coming_soon,
            "属性": self.coming_soon,
            "黄历": self.coming_soon,
            "运势": self.coming_soon,
            "账号": self.account_menu_command,
            "联系": self.coming_soon
        }
        
        if content in raw_commands:
            await raw_commands[content](update, context)
    
    async def show_register_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📝 **注册账号 | Register Account**\n\n"
            "使用命令 | Use command:\n"
            "`/register <用户名> <语言>`\n\n"
            "例如 | Example:\n"
            "`/register 张三 CHS`",
            parse_mode='Markdown'
        )
    
    async def coming_soon(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🚧 **功能开发中 | Feature Under Development**\n\n"
            "该功能即将推出，敬请期待！\n"
            "This feature is coming soon, stay tuned!"
        )
    
    async def version_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"🤖 **XiuXianBot Telegram Adapter**\n"
            f"版本 | Version: {self.version}\n"
            f"平台 | Platform: Telegram"
        )
    
    async def verify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 1:
            await update.message.reply_text(
                "使用方法 | Usage: /verify <OTP_CODE>\n"
                "例如 | Example: /verify 123456"
            )
            return
        
        otp_code = args[0].strip()
        
        try:
            from core.utils.otp import verify_otp, link_platform_account
            
            user_id = str(update.effective_user.id)
            
            if verify_otp(user_id, otp_code, purpose='account_link'):
                if link_platform_account(user_id, 'telegram', user_id):
                    await update.message.reply_text("✅ 账号关联成功！| Account linked successfully!")
                else:
                    await update.message.reply_text("❌ 账号关联失败 | Account linking failed")
            else:
                await update.message.reply_text("❌ 验证码无效或已过期 | Invalid or expired OTP")
                
        except Exception as e:
            logger.error(f"Error in verify command: {e}")
            await update.message.reply_text("❌ 验证过程中出现错误 | Error during verification")

    async def unlink_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 1 or args[0].lower() not in ['discord', 'telegram', 'matrix']:
            await update.message.reply_text(
                "使用方法 | Usage: /unlink <platform>\n"
                "平台选项 | Platform options: discord, telegram, matrix"
            )
            return
        
        platform = args[0].strip().lower()
        
        try:
            from core.utils.otp import unlink_platform_account
            
            user_id = str(update.effective_user.id)
            
            if unlink_platform_account(user_id, platform):
                await update.message.reply_text(f"✅ 已取消 {platform.title()} 平台关联 | {platform.title()} account unlinked successfully")
            else:
                await update.message.reply_text(f"❌ 取消关联失败 | Failed to unlink {platform} account")
                
        except Exception as e:
            logger.error(f"Error in unlink command: {e}")
            await update.message.reply_text("❌ 取消关联过程中出现错误 | Error during unlinking")

    async def account_menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = str(update.effective_user.id)
            user_collection = get_collection('users')
            user = user_collection.find_one({"user_id": user_id})
        except DatabaseError:
            await update.message.reply_text("Database Error! Contact Bot admins!")
            return

        if not user:
            await update.message.reply_text(
                "❌ 未找到账号，请先注册\n"
                "No account found, please register first\n\n"
                "使用 /register 注册账号\nUse /register to create account"
            )
            return

        third_party_ids = user.get('third_party_ids', {})
        platform_info = []
        
        for platform, platform_id in third_party_ids.items():
            if platform_id and platform_id.strip():
                platform_info.append(f"✅ {platform.title()}: `{platform_id}`")
            else:
                platform_info.append(f"❌ {platform.title()}: 未关联 | Not linked")
        
        account_text = (
            f"👤 **账号管理 | Account Management**\n\n"
            f"**用户信息 | User Info:**\n"
            f"• 用户名 | Username: {user.get('in_game_username', 'N/A')}\n"
            f"• UID: `{user_id}`\n"
            f"• 语言 | Language: {user.get('lang', 'CHS')}\n\n"
            f"**平台关联 | Platform Links:**\n"
            f"{chr(10).join(platform_info)}\n\n"
            f"**可用命令 | Available Commands:**\n"
            f"• `/link <UID> [platform]` - 关联账号\n"
            f"• `/unlink <platform>` - 取消关联\n"
            f"• `/verify <OTP>` - 验证关联"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("关联账号 | Link", callback_data="link"),
                InlineKeyboardButton("查看状态 | Status", callback_data="check_status")
            ],
            [
                InlineKeyboardButton("返回主菜单 | Main", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            account_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def run(self):
        await self.setup_commands()
    
        logger.info("Starting Telegram bot...")
        async with self.application:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
            finally:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()


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

    token = config.get('tokens', {}).get('telegram_token')
    if not token:
        logger.error("Telegram token not found in config")
        return

    bot = XiuXianTelegramBot(token)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")

if __name__ == "__main__":
    main()
