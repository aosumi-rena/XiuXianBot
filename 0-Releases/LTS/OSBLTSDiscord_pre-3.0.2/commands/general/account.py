import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput, Button, View
import json, time

from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation

def load_codes():
    try:
        with open("textmaps/codes.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("codes.json not found! Make sure the file exists.")
        return {"codes": []}
    except Exception as e:
        print(f"Error loading codes.json: {e}")
        return {"codes": []}

class RedeemCodeModal(Modal):
    def __init__(self, user_id, user_collection, items_collection, user_lang):
        super().__init__(title="兑换码 | Redeem Code")
        self.user_id = user_id
        self.user_collection = user_collection
        self.items_collection = items_collection
        self.user_lang = user_lang

        self.code_input = TextInput(
            label="请输入兑换码 (Enter Redeem Code)",
            placeholder="Code Here (Case-insensitive)",
            style=discord.TextStyle.short
        )
        self.add_item(self.code_input)

    async def on_submit(self, interaction: discord.Interaction):
        entered_code = self.code_input.value.strip().upper()

        codes_data = load_codes()
        all_codes = codes_data.get("codes", [])

        matched_code = None
        for c in all_codes:
            if c["code"].upper() == entered_code:
                matched_code = c
                break

        if not matched_code:
            _, msg = get_response("redeem_code_not_found", lang=self.user_lang)
            await interaction.response.send_message(msg, ephemeral=True)
            return

        current_ts = int(time.time())
        start_ts = matched_code.get("start_ts", 0)
        end_ts = matched_code.get("end_ts", 0)

        if current_ts < start_ts or current_ts > end_ts:
            _, msg = get_response("redeem_code_expired", lang=self.user_lang)
            await interaction.response.send_message(msg, ephemeral=True)
            return

        allowed_users = matched_code.get("allowed_users", [])
        if "*" not in allowed_users and str(self.user_id) not in allowed_users:
            _, msg = get_response("redeem_code_not_allowed", lang=self.user_lang)
            await interaction.response.send_message(msg, ephemeral=True)
            return

        user_data = self.user_collection.find_one({"user_id": str(self.user_id)})
        if not user_data:
            _, msg = get_response("redeem_code_no_user", lang=self.user_lang)
            await interaction.response.send_message(msg, ephemeral=True)
            return

        user_codes = user_data.get("codes", {})
        if user_codes.get(matched_code["code"], False):
            # Already redeemed
            _, msg = get_response("redeem_code_already", lang=self.user_lang)
            await interaction.response.send_message(msg, ephemeral=True)
            return

        content = matched_code.get("content", {})
        copper_to_add = content.get("copper", 0)
        gold_to_add = content.get("gold", 0)
        items_to_add = content.get("items", {})

        new_copper = user_data.get("copper", 0) + copper_to_add
        new_gold = user_data.get("gold", 0) + gold_to_add

        self.user_collection.update_one(
            {"user_id": str(self.user_id)},
            {
                "$set": {
                    "copper": new_copper,
                    "gold": new_gold,
                    f"codes.{matched_code['code']}": True
                }
            }
        )

        for item_id_str, qty in items_to_add.items():
            item_id = int(item_id_str)
            existing_item = self.items_collection.find_one({"owner": int(self.user_id), "item": item_id})
            if existing_item:
                new_quantity = existing_item.get("quantity", 0) + qty
                self.items_collection.update_one(
                    {"_id": existing_item["_id"]},
                    {"$set": {"quantity": new_quantity}}
                )
            else:
                self.items_collection.insert_one({
                    "owner": int(self.user_id),
                    "item": item_id,
                    "quantity": qty
                })

        textmap = load_localisation(self.user_lang)
        items_section = ""
        if items_to_add:
            item_lines = []
            for item_id_str, quantity in items_to_add.items():
                item_name = textmap["items"].get(item_id_str, f"Item#{item_id_str}")
                item_lines.append(f"{item_name} x {quantity}")
            items_section = "\nItems/物品: " + ", ".join(item_lines)

        _, success_msg = get_response(
            "redeem_code_success",
            lang=self.user_lang.upper(),
            copper_gained=copper_to_add,
            gold_gained=gold_to_add,
            items_section=items_section
        )

        await interaction.response.send_message(success_msg, ephemeral=True)

class AccountUpdateModal(Modal):
    def __init__(self, user_id, username, user_collection):
        super().__init__(title="修改账号 | Update Account")
        self.user_id = user_id
        self.username = username
        self.user_collection = user_collection

        self.add_item(
            TextInput(
                label="游戏用户名 - Enter New Username",
                placeholder="你的游戏名 | Your Username",
                style=discord.TextStyle.short
            )
        )
        self.add_item(
            TextInput(
                label="选择语言 - Choose Lang (EN/CHS)",
                placeholder="EN/CHS",
                style=discord.TextStyle.short
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        new_in_game_username = self.children[0].value.strip()
        new_language = self.children[1].value.strip().upper()

        if len(new_in_game_username) > 40:
            await interaction.response.send_message(
                "## Update Failed! | 更新失败！\n用户名不能超过40个字符，请缩短您的用户名。\nUsername cannot exceed 40 characters, please shorten it.",
                ephemeral=True
            )
            return

        if new_language not in ["EN", "CHS"]:
            await interaction.response.send_message(
                "## Update Failed! | 更新失败！\n语言无效，请输入 EN 或 CHS\nInvalid language format, enter one of the following: EN / CHS",
                ephemeral=True
            )
            return

        self.user_collection.update_one(
            {"user_id": self.user_id},
            {
                "$set": {
                    "in_game_username": new_in_game_username,
                    "lang": new_language
                }
            }
        )

        await interaction.response.send_message(
            f"账号已更新！新用户名：{new_in_game_username}，语言已切换为 {new_language}。\n"
            f"Account updated!, your new username is {new_in_game_username}, and language has been switched to {new_language}.",
            ephemeral=True
        )

class AccountUpdateView(View):
    def __init__(self, update_modal, redeem_modal, timeout=60):
        super().__init__(timeout=timeout)
        self.update_modal = update_modal
        self.redeem_modal = redeem_modal

    @discord.ui.button(
        label="更改账号信息 | Change Account Details",
        style=discord.ButtonStyle.primary
    )
    async def open_update_form(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(self.update_modal)

    @discord.ui.button(
        label="兑换码 | Redeem Codes",
        style=discord.ButtonStyle.secondary
    )
    async def redeem_codes(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(self.redeem_modal)

class AccountCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="acc", description="Change your account details.")
    async def acc_command(self, interaction: discord.Interaction):
        try:
            user_collection = get_collection('users')
            items_collection = get_collection('items')
        except DatabaseError:
            await interaction.response.send_message(
                "Database Error! Contact Bot admins!",
                ephemeral=True
            )
            return

        user_id = str(interaction.user.id)
        username = interaction.user.name

        if interaction.guild is not None:
            user_data = user_collection.find_one({"user_id": user_id})
            user_lang = user_data.get("lang", "CHS")
            response_type, text = get_response("privacy", lang=user_lang)
            await interaction.response.send_message(content=text, ephemeral=True)
            return

        user_data = user_collection.find_one({"user_id": user_id})
        if not user_data:
            await interaction.response.send_message(
                "您还没有创建账号，请使用`开始`（`^ks`、`^start`、`^begin`）指令创建账号！（推荐：在Bot私聊/DM使用此指令，以最大化保护您的隐私。）\n"
                "You have not created an account yet, Please use `^start` or `^begin` to create one. "
                "(Recommendation: Use this command in Bot DM for maximum privacy protection.)",
                ephemeral=True
            )
            return

        in_game_username = user_data.get("in_game_username", username)
        user_lang = user_data.get("lang", "CHS")
        element = user_data.get("element", "无 | None")
        localization = load_localisation(user_lang)
        if user_lang.upper() != "CHS":
            element = localization.get("elements", {}).get(element, element)
        response_type, embed_text = get_response(
            "account_setting",
            user=in_game_username,
            uid=user_id,
            acc_lang=user_lang,
            element=element,
            lang=user_lang
        )

        embed = discord.Embed(
            title=f"{in_game_username}",
            description=embed_text,
            color=discord.Color.blue()
        )

        update_modal = AccountUpdateModal(user_id, username, user_collection)
        redeem_modal = RedeemCodeModal(user_id, user_collection, items_collection, user_lang)

        view = AccountUpdateView(update_modal=update_modal, redeem_modal=redeem_modal, timeout=None)

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(AccountCommand(bot))
