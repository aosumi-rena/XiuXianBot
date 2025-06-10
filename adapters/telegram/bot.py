import os
import sys
import logging
import json
import aiohttp
from functools import wraps

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.utils.localisation import get_response, load_localisation
from core.utils.account_status import format_status_text

LOG_DIR = os.path.abspath(os.path.join(ROOT_DIR, "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "telegram.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("telegram")
DEFAULT_SERVER_PORT = 11450
SERVER_URL = f"http://127.0.0.1:{DEFAULT_SERVER_PORT}"


async def http_get(url, **kwargs):
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, **kwargs) as resp:
            return await resp.json()


async def http_post(url, **kwargs):
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, **kwargs) as resp:
            return await resp.json()


def require_account(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        try:
            r = await http_get(
                f"{SERVER_URL}/api/user/lookup",
                params={"platform": "telegram", "platform_id": user_id},
                timeout=15,
            )
            if not r.get("success"):
                _, text = get_response(
                    "no_account",
                    user=update.effective_user.mention_html(),
                    lang="CHS",
                    platform="telegram",
                )
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
                return
            context.user_data["uid"] = r["user_id"]
            context.user_data["lang"] = r.get("lang", "CHS")
            context.user_data["username"] = r.get("username", update.effective_user.first_name)
        except Exception as exc:
            logger.error(f"lookup error: {exc}")
            await update.message.reply_text("Server error")
            return
        await handler(update, context)
    return wrapper


async def register_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        r = await http_get(
            f"{SERVER_URL}/api/user/lookup",
            params={"platform": "telegram", "platform_id": user_id},
            timeout=15,
        )
        if r.get("success"):
            lang = r.get("lang", "CHS")
            username = r.get("username", update.effective_user.first_name)
            _, text = get_response(
                "already_account",
                user=username,
                lang=lang,
                platform="telegram",
            )
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            return
    except Exception as exc:
        logger.error(f"lookup error: {exc}")

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /register <username> <lang>")
        return
    username = context.args[0].strip()
    lang = context.args[1].strip().upper() or "CHS"
    payload = {
        "platform": "telegram",
        "platform_id": user_id,
        "username": username,
        "lang": lang,
    }
    try:
        data = await http_post(f"{SERVER_URL}/api/register", json=payload, timeout=15)
        if data.get("success"):
            await update.message.reply_text(f"✅ UID: {data['user_id']}")
        else:
            await update.message.reply_text(f"❌ {data.get('message', 'error')}")
    except Exception as exc:
        logger.error(f"register error: {exc}")
        await update.message.reply_text("Server error")


@require_account
async def stat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = context.user_data["uid"]
    lang = context.user_data["lang"]
    try:
        r = await http_get(f"{SERVER_URL}/api/stat/{uid}", timeout=15)
        if r.get("success"):
            status = r["status"]
            text = format_status_text(status, lang, platform="telegram")
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            return
    except Exception as exc:
        logger.error(f"status error: {exc}")
    await update.message.reply_text("Error fetching status")


@require_account
async def cultivate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = context.user_data["uid"]
    lang = context.user_data["lang"]
    action = context.args[0] if context.args else None
    try:
        status = await http_get(f"{SERVER_URL}/api/cultivate/status/{uid}", timeout=15)
        cultivating = status.get("state", False)
        if action == "stat":
            if not cultivating:
                await update.message.reply_text("未在修炼 | Not cultivating")
            else:
                current = status.get("current_gain")
                await update.message.reply_text(f"修炼中，已获得 {current} 修为")
            return
        if (action == "start" or action is None) and not cultivating:
            data = await http_post(
                f"{SERVER_URL}/api/cultivate/start",
                json={"user_id": uid},
                timeout=15,
            )
            if data.get("success"):
                _, text = get_response(
                    "cultivation_start",
                    user=context.user_data.get("username", update.effective_user.first_name),
                    lang=lang,
                    platform="telegram",
                )
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(data.get("message", "Error"))
            return
        if (action == "end" or action is None) and cultivating:
            data = await http_post(f"{SERVER_URL}/api/cultivate/end", json={"user_id": uid}, timeout=15)
            if data.get("success"):
                _, text = get_response(
                    "cultivation_end",
                    culti_gain=data["gain"],
                    lang=lang,
                    platform="telegram",
                )
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(data.get("message", "Error"))
            return
        await update.message.reply_text("❌ 无效操作 | Invalid action")
    except Exception as exc:
        logger.error(f"cultivate error: {exc}")
        await update.message.reply_text("Server error")


def load_config():
    path = os.path.join(ROOT_DIR, "config.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error(f"Failed to load config: {exc}")
        return None


def main():
    cfg = load_config()
    if not cfg:
        return
    global SERVER_URL
    port = cfg.get("core_server", {}).get("port", DEFAULT_SERVER_PORT)
    SERVER_URL = f"http://127.0.0.1:{port}"
    token = cfg.get("tokens", {}).get("telegram_token")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("register", register_cmd))
    app.add_handler(CommandHandler(["stat", "status"], stat_cmd))
    app.add_handler(CommandHandler(["cul", "cultivate"], cultivate_cmd))

    commands = [
        BotCommand("register", "Create account"),
        BotCommand("stat", "Show status"),
        BotCommand("cul", "Cultivate"),
    ]
    try:
        app.bot.set_my_commands(commands)
    except Exception:
        pass

    logger.info("Starting telegram bot")
    app.run_polling()


if __name__ == "__main__":
    main()
