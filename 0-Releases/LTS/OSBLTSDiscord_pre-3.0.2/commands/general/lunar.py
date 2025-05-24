import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import datetime
import cnlunar

class LunarCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="luck", description="Daily Luckiness. 今日运势")
    async def luck(self, interaction: discord.Interaction):
        """Command to check your daily luck."""
        vote_button = Button(label="💎Vote", url="https://top.gg/bot/1271440212832161846")
        view = View()
        view.add_item(vote_button)

        request = str(interaction.user)
        today = datetime.date.today()
        day, month, year = today.day, today.month, today.year
        user_id = interaction.user.id

        long_number_int = int(f"{user_id}")
        initial = (long_number_int / (day + month + year)) % 101

        result = (
            initial + 50 if initial <= 20 else
            98.55 if initial >= 100 else
            initial
        )

        result_percentage = result

        if result >= 80:
            luckiness_chs = "大吉"
            luckiness_en = "Great Fortune"
        elif result >= 70:
            luckiness_chs = "中吉"
            luckiness_en = "Medium Fortune"
        elif result >= 60:
            luckiness_chs = "小吉"
            luckiness_en = "Little Fortune"
        elif result >= 50:
            luckiness_chs = "吉"
            luckiness_en = "Slightly Fortune"
        elif result >= 40:
            luckiness_chs = "末吉"
            luckiness_en = "Just Good Fortune"
        elif result > 100:
            luckiness_chs = "错误，请联系Bot管理"
            luckiness_en = "This is an ERROR, contact Bot admins."
        else:
            luckiness_chs = "大凶" if result < 25 else "凶"
            luckiness_en = "Misfortune" if result < 25 else "Great Misfortune"

        lunar = cnlunar.Lunar(datetime.datetime(year, month, day), godType='8char')
        good_thing = lunar.goodThing or []
        bad_thing = lunar.badThing or []
        lucky_timing = lunar.get_twohourLuckyList()

        time_ranges = []
        i, n = 0, len(lucky_timing)
        while i < n:
            if lucky_timing[i] == '吉':
                start_time = 23 if i == 0 else (1 + (i - 1) * 2) % 24
                j = i
                while j + 1 < n and lucky_timing[j + 1] == '吉':
                    j += 1
                end_time = 1 if j == 12 else (1 + (j - 1) * 2 + 2) % 24
                time_ranges.append(f"{start_time:02d}00-{end_time:02d}00" if end_time != 0 else "0000")
                i = j + 1
            else:
                i += 1

        lucky_time_ranges = '、'.join(time_ranges) if time_ranges else '<ERROR>'
        good_thing_str = '、'.join(good_thing) if good_thing else '<ERROR>'
        bad_thing_str = '、'.join(bad_thing) if bad_thing else '<ERROR>'

        embed = discord.Embed(
            title="穷观阵 —— 今日运势",
            description=f"""
**今日运势：{luckiness_chs}**
**Today's Fortune: {luckiness_en}**
```运气值 / Luckiness Value：{result_percentage:.2f}%```
宜：{good_thing_str}

忌：{bad_thing_str}

吉时：{lucky_time_ranges}
""",
            color=0x00f2ff
        )
        embed.set_author(name="穷观阵")
        embed.set_footer(text=f"Requested by {request} ({day} {month} {year})")
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="lunar", description="Get Lunar information for a specific date and time.")
    @app_commands.describe(
        year="Year (e.g., 2022)",
        month="Month (1-12)",
        day="Day (1-31)",
        hour="Hour (0-23)",
        minute="Minute (0-59)"
    )
    async def lunar(
        self,
        interaction: discord.Interaction,
        year: int = None,
        month: int = None,
        day: int = None,
        hour: int = None,
        minute: int = None
    ):
        """Command to get Lunar information."""
        now = datetime.datetime.now()
        year = year or now.year
        month = month or now.month
        day = day or now.day
        hour = hour or now.hour
        minute = minute or now.minute

        lunar_date = datetime.datetime(year, month, day, hour, minute)
        lunar = cnlunar.Lunar(lunar_date, godType="8char")

        dic = {
            '农历': f"{lunar.lunarYearCn} {lunar.year8Char}[{lunar.chineseYearZodiac}]年 {lunar.lunarMonthCn}{lunar.lunarDayCn}",
            '星期': lunar.weekDayCn,
            '今日节日': (lunar.get_legalHolidays(), lunar.get_otherHolidays(), lunar.get_otherLunarHolidays()),
            '八字': ' '.join([lunar.year8Char, lunar.month8Char, lunar.day8Char, lunar.twohour8Char]),
            '下一节气': (lunar.nextSolarTerm, lunar.nextSolarTermDate, lunar.nextSolarTermYear),
            '今年节气表': lunar.thisYearSolarTermsDic,
            '季节': lunar.lunarSeason,
            '时辰凶吉': lunar.get_twohourLuckyList(),
            '生肖冲煞': lunar.chineseZodiacClash,
            '星座': lunar.starZodiac,
            '星次': lunar.todayEastZodiac,
            '彭祖百忌': lunar.get_pengTaboo(),
            '十二神': lunar.get_today12DayOfficer(),
            '廿八宿': lunar.get_the28Stars(),
            '今日三合': lunar.zodiacMark3List,
            '今日六合': lunar.zodiacMark6,
            '今日五行': lunar.get_today5Elements(),
            '纳音': lunar.get_nayin(),
            '九宫飞星': lunar.get_the9FlyStar(),
            '吉神方位': lunar.get_luckyGodsDirection(),
            '今日胎神': lunar.get_fetalGod(),
            '神煞宜忌': lunar.angelDemon,
            '今日吉神': lunar.goodGodName,
            '今日凶煞': lunar.badGodName,
            '宜忌等第': lunar.todayLevelName,
            '宜': lunar.goodThing,
            '忌': lunar.badThing,
            '时辰经络': lunar.meridians,
        }

        embeds = []
        field_list = list(dic.items())
        max_fields_per_embed = 25

        embed = discord.Embed(
            title="农历信息",
            description=f"请求时间: {lunar_date.strftime('%Y-%m-%d %H:%M')}",
            color=0x00f2ff
        )
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        embeds.append(embed)

        for i in range(0, len(field_list), max_fields_per_embed):
            sub_embed = discord.Embed(color=0x00f2ff)
            for key, value in field_list[i:i + max_fields_per_embed]:
                value_str = str(value)[:1024] if len(str(value)) > 1024 else str(value)
                sub_embed.add_field(name=key, value=value_str, inline=False)
            embeds.append(sub_embed)

        await interaction.response.send_message(embeds=embeds)

async def setup(bot):
    await bot.add_cog(LunarCommands(bot))
