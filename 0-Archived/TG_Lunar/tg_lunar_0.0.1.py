import datetime
import uuid
import logging

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    InlineQueryHandler,
    CommandHandler,
    ContextTypes,
)
from telegram.helpers import escape_markdown

import cnlunar

BOT_TOKEN = "REDACTED"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def escape_dash(text: str) -> str:
    return text.replace('-', '\\-')

# /start 
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                text="今日运势",
                switch_inline_query_current_chat="luck"
            ),
            InlineKeyboardButton(
                text="黄历信息",
                switch_inline_query_current_chat="lunar"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text="这是开始信息",
        reply_markup=reply_markup
    )

async def generate_luck_response(user_id, year, month, day, daily_offset):
    long_number_int = int(user_id)
    initial = (long_number_int + daily_factor(user_id, day, month, year)) % 101
    base_luck = (initial + 50) if initial <= 20 else (98.55) if initial >= 100 else initial
    luck_value = min(base_luck + daily_offset, 100)
    result = round(luck_value, 2)

    if result >= 80:
        luckiness_chs = "大吉"
    elif result >= 70:
        luckiness_chs = "中吉"
    elif result >= 60:
        luckiness_chs = "小吉"
    elif result >= 50:
        luckiness_chs = "吉"
    elif result >= 40:
        luckiness_chs = "末吉"
    else:
        luckiness_chs = "大凶" if result < 25 else "凶"

    lunar_for_luck = cnlunar.Lunar(datetime.datetime(year, month, day), godType='8char')
    good_thing = lunar_for_luck.goodThing or []
    bad_thing = lunar_for_luck.badThing or []
    lucky_timing = lunar_for_luck.get_twohourLuckyList()

    time_ranges = []
    i, n = 0, len(lucky_timing)
    while i < n:
        if lucky_timing[i] == '吉':
            start_time = 23 if i == 0 else (1 + (i - 1) * 2) % 24
            j = i
            while j + 1 < n and lucky_timing[j + 1] == '吉':
                j += 1
            end_time = 1 if j == 12 else (1 + (j - 1) * 2 + 2) % 24
            time_range = f"{start_time:02d}00\\-{end_time:02d}00" if end_time != 0 else "0000"
            time_ranges.append(time_range)
            i = j + 1
        else:
            i += 1

    good_thing_str = '、'.join(good_thing) if good_thing else '<未知>'
    bad_thing_str = '、'.join(bad_thing) if bad_thing else '<未知>'
    lucky_time_ranges = '、'.join(time_ranges) if time_ranges else '<未知>'

    luck_text = (
        f"**今日运势：{luckiness_chs}**\n"
        f"**运气值**：`{result:.2f}%`\n\n"
        f"宜：\n```{good_thing_str}```\n"
        f"忌：\n```{bad_thing_str}```\n"
        f"吉时：`{lucky_time_ranges}`\n"
        "其他黄历信息：使用`@RelFuXuanBot lunar`查看"
    )

    return luckiness_chs, result, luck_text

def daily_factor(user_id, day, month, year):
    random_factor = hash((user_id, day, month, year)) % 1000
    return random_factor

async def generate_lunar_response(now):
    lunar_date = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
    lunar_for_lunar = cnlunar.Lunar(lunar_date, godType="8char")

    data_dict_lunar = {
        "农历": f"{lunar_for_lunar.lunarYearCn} {lunar_for_lunar.year8Char}[{lunar_for_lunar.chineseYearZodiac}]年 {lunar_for_lunar.lunarMonthCn}{lunar_for_lunar.lunarDayCn}",
        "八字": " ".join([
            lunar_for_lunar.year8Char,
            lunar_for_lunar.month8Char,
            lunar_for_lunar.day8Char,
            lunar_for_lunar.twohour8Char
        ]),
        "下一节气": str((lunar_for_lunar.nextSolarTerm, lunar_for_lunar.nextSolarTermDate, lunar_for_lunar.nextSolarTermYear)),
        "今年节气表": f"{lunar_for_lunar.thisYearSolarTermsDic}",
        "季节": lunar_for_lunar.lunarSeason,
        "宜": "使用@RelFuXuanBot luck查看",
        "忌": "使用@RelFuXuanBot luck查看",
        "时辰凶吉": "使用@RelFuXuanBot luck查看",
        "生肖冲煞": lunar_for_lunar.chineseZodiacClash,
        "星座": lunar_for_lunar.starZodiac,
        "星次": lunar_for_lunar.todayEastZodiac,
        "彭祖百忌": lunar_for_lunar.get_pengTaboo(),
        "十二神": lunar_for_lunar.get_today12DayOfficer(),
        "廿八宿": lunar_for_lunar.get_the28Stars(),
        "今日三合": lunar_for_lunar.zodiacMark3List,
        "今日六合": lunar_for_lunar.zodiacMark6,
        "今日五行": lunar_for_lunar.get_today5Elements(),
        "纳音": lunar_for_lunar.get_nayin(),
        "今日吉神": lunar_for_lunar.goodGodName,
        "吉神方位": lunar_for_lunar.get_luckyGodsDirection(),
        "今日凶煞": lunar_for_lunar.badGodName,
        "九宫飞星": lunar_for_lunar.get_the9FlyStar(),
        "时辰经络": lunar_for_lunar.meridians,
    }

    escaped_data_dict_lunar = {k: escape_markdown(str(v), version=2) for k, v in data_dict_lunar.items()}

    lines_lunar = [f"> **{k}**: `{v}`" for k, v in escaped_data_dict_lunar.items()]

    escaped_time = escape_dash(now.strftime('%Y-%m-%d %H:%M'))

    lunar_text_raw = f"**> **今日黄历信息**（请求时间：{escaped_time}）\n" + "\n".join(lines_lunar)

    return lunar_text_raw

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query.strip()
    user = update.inline_query.from_user

    today = datetime.date.today()
    day, month, year = today.day, today.month, today.year
    user_id = user.id
    random_factor = daily_factor(user_id, day, month, year)
    float_offset_seed = hash((user_id, year, month, day, 'floatoffset')) % 100
    daily_offset = float_offset_seed / 100.0

    try:
        if not query:
            logger.info("Handling empty query for user ID: %s", user_id)

            luckiness_chs, result, luck_text = await generate_luck_response(user_id, year, month, day, daily_offset)

            luck_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="今日运势",
                        switch_inline_query_current_chat="luck"
                    )
                ]
            ])
            luck_article = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="今日运势",
                description=f"{luckiness_chs} ({result:.2f}%)",
                input_message_content=InputTextMessageContent(
                    luck_text,
                    parse_mode="MarkdownV2"
                ),
                reply_markup=luck_keyboard
            )

            now = datetime.datetime.now()
            lunar_text = await generate_lunar_response(now)

            lunar_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="黄历信息",
                        switch_inline_query_current_chat="lunar"
                    )
                ]
            ])
            lunar_article = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="黄历信息",
                description=f"农历：{cnlunar.Lunar(now, godType='8char').lunarMonthCn}{cnlunar.Lunar(now, godType='8char').lunarDayCn}",
                input_message_content=InputTextMessageContent(
                    lunar_text,
                    parse_mode="MarkdownV2"
                ),
                reply_markup=lunar_keyboard
            )

            await update.inline_query.answer([luck_article, lunar_article], cache_time=0)
            return

        elif query.lower().startswith("luck"):
            logger.info("Handling 'luck' query for user ID: %s", user_id)
            
            luckiness_chs, result, luck_text = await generate_luck_response(user_id, year, month, day, daily_offset)

            luck_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="今日运势",
                        switch_inline_query_current_chat="luck"
                    )
                ]
            ])
            luck_article = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="今日运势",
                description=f"{luckiness_chs} ({result:.2f}%)",
                input_message_content=InputTextMessageContent(
                    luck_text,
                    parse_mode="MarkdownV2"
                ),
                reply_markup=luck_keyboard
            )

            await update.inline_query.answer([luck_article], cache_time=0)
            return

        elif query.lower().startswith("lunar"):
            logger.info("Handling 'lunar' query for user ID: %s", user_id)
            
            now = datetime.datetime.now()
            lunar_text = await generate_lunar_response(now)

            lunar_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="黄历信息",
                        switch_inline_query_current_chat="lunar"
                    )
                ]
            ])
            lunar_article = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="黄历信息",
                description=f"农历：{cnlunar.Lunar(now, godType='8char').lunarMonthCn}{cnlunar.Lunar(now, godType='8char').lunarDayCn}",
                input_message_content=InputTextMessageContent(
                    lunar_text,
                    parse_mode="MarkdownV2"
                ),
                reply_markup=lunar_keyboard
            )

            await update.inline_query.answer([lunar_article], cache_time=0)
            return

        else:
            logger.warning("Unknown query received: %s", query)
            await update.inline_query.answer([], cache_time=0)
            return

    except Exception as e:
        logger.exception("Exception occurred in inline_query: %s", e)
        await update.inline_query.answer([], cache_time=0)

from telegram.ext import MessageHandler, filters

async def handle_exact_queries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text.strip().lower()
    user = update.message.from_user

    today = datetime.date.today()
    day, month, year = today.day, today.month, today.year
    user_id = user.id
    random_factor = daily_factor(user_id, day, month, year)
    float_offset_seed = hash((user_id, year, month, day, 'floatoffset')) % 100
    daily_offset = float_offset_seed / 100.0

    try:
        if message == "luck" or message == "@bot luck":
            logger.info("Handling exact 'luck' query for user ID: %s", user_id)
            
            luckiness_chs, result, luck_text = await generate_luck_response(user_id, year, month, day, daily_offset)

            luck_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="今日运势",
                        switch_inline_query_current_chat="luck"
                    )
                ]
            ])
            luck_article = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="今日运势",
                description=f"{luckiness_chs} ({result:.2f}%)",
                input_message_content=InputTextMessageContent(
                    luck_text,
                    parse_mode="MarkdownV2"
                ),
                reply_markup=luck_keyboard
            )

            await update.message.reply_text(
                luck_text,
                parse_mode="MarkdownV2",
                reply_markup=luck_keyboard
            )
            return

        elif message == "lunar" or message == "@bot lunar":
            logger.info("Handling exact 'lunar' query for user ID: %s", user_id)
            
            now = datetime.datetime.now()
            lunar_text = await generate_lunar_response(now)

            lunar_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="黄历信息",
                        switch_inline_query_current_chat="lunar"
                    )
                ]
            ])
            lunar_article = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="黄历信息",
                description=f"农历：{cnlunar.Lunar(now, godType='8char').lunarMonthCn}{cnlunar.Lunar(now, godType='8char').lunarDayCn}",
                input_message_content=InputTextMessageContent(
                    lunar_text,
                    parse_mode="MarkdownV2"
                ),
                reply_markup=lunar_keyboard
            )

            await update.message.reply_text(
                lunar_text,
                parse_mode="MarkdownV2",
                reply_markup=lunar_keyboard
            )
            return

    except Exception as e:
        logger.exception("Exception occurred in handle_exact_queries: %s", e)
        await update.message.reply_text(f"Error: {e}")

# Main 
def main():
    print("Starting bot now...")

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exact_queries))

    application.run_polling()

if __name__ == "__main__":
    main()