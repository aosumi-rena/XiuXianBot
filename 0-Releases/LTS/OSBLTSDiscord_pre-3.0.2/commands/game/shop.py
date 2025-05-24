import discord
from discord.ext import commands
from discord.ui import Button, View
import json

from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation


def load_shop():
    try:
        with open("textmaps/shop.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("shop_items", [])
    except FileNotFoundError:
        print("shop.json not found!")
        return []
    except Exception as e:
        print(f"Error loading shop.json: {e}")
        return []


class ShopView(View):
    def __init__(self, ctx, shop_items, user_lang, page=1, max_per_page=5):
        super().__init__()
        self.ctx = ctx
        self.shop_items = shop_items
        self.user_lang = user_lang
        self.page = page
        self.max_per_page = max_per_page
        self.total_pages = (len(shop_items) + max_per_page - 1) // max_per_page
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        if self.page > 1:
            self.add_item(Button(label="◀️", style=discord.ButtonStyle.primary, custom_id="prev"))
        if self.page < self.total_pages:
            self.add_item(Button(label="▶️", style=discord.ButtonStyle.primary, custom_id="next"))

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.ctx.author

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

    async def prev_callback(self, interaction: discord.Interaction):
        self.page -= 1
        self.update_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_callback(self, interaction: discord.Interaction):
        self.page += 1
        self.update_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_embed(self):
        textmap = load_localisation(self.user_lang)

        start = (self.page - 1) * self.max_per_page
        end = start + self.max_per_page
        page_items = self.shop_items[start:end]

        _, shop_title = get_response("shop_title", lang=self.user_lang)
        _, shop_view_desc = get_response("shop_view_description", lang=self.user_lang)

        if not page_items:
            _, no_items_text = get_response("shop_no_items", lang=self.user_lang)
            description = no_items_text
        else:
            lines = []
            for itm in page_items:
                item_name = textmap["items"].get(str(itm["item_id"]), f"NO_TEXT(Item#{itm['item_id']})")
                localized_currency = textmap["currency_display"].get(itm["currency"], itm["currency"])

                _, line = get_response(
                    "shop_view_table_line",
                    shop_item_id=itm["shop_item_id"],
                    item_name=item_name,
                    quantity=itm["quantity"],
                    price=itm["price"],
                    currency=localized_currency,
                    lang=self.user_lang
                )
                lines.append(line)

            description = shop_view_desc + "\n\n" + "\n".join(lines)

        embed = discord.Embed(
            title=shop_title,
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {self.page} of {self.total_pages}")
        return embed


class ConfirmBuyView(View):
    def __init__(self, ctx, user_lang, shop_item):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.user_lang = user_lang
        self.shop_item = shop_item

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.ctx.author

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: Button):
        user_collection = get_collection("users")
        items_collection = get_collection("items")

        user_id = str(self.ctx.author.id)
        user = user_collection.find_one({"user_id": user_id})
        if not user:
            await interaction.response.send_message(
                f"{self.ctx.author.mention} 您还没有创建账号，请使用 `^start` 指令创建账号！",
                ephemeral=True
            )
            self.stop()
            return

        currency_type = self.shop_item["currency"]
        price = self.shop_item["price"]
        item_id = self.shop_item["item_id"]
        quantity = self.shop_item["quantity"]

        textmap = load_localisation(self.user_lang)
        localized_currency = textmap["currency_display"].get(currency_type, currency_type)
        item_name = textmap["items"].get(str(item_id), f"NO_TEXT(Item#{item_id})")

        user_currency_value = user.get(currency_type, 0)
        if user_currency_value < price:
            _, insufficient_msg = get_response(
                "shop_buy_insufficient_funds",
                currency=localized_currency,
                item_name=item_name,
                lang=self.user_lang
            )
            await interaction.response.send_message(insufficient_msg, ephemeral=True)
            self.stop()
            return

        new_value = user_currency_value - price
        user_collection.update_one(
            {"user_id": user_id},
            {"$set": {currency_type: new_value}}
        )

        existing_item = items_collection.find_one({"owner": int(user_id), "item": item_id})
        if existing_item:
            new_qty = existing_item.get("quantity", 0) + quantity
            items_collection.update_one(
                {"_id": existing_item["_id"]},
                {"$set": {"quantity": new_qty}}
            )
        else:
            items_collection.insert_one({
                "owner": int(user_id),
                "item": item_id,
                "quantity": quantity
            })

        _, success_template = get_response(
            "shop_buy_success",
            item_name=item_name,
            quantity=quantity,
            price=price,
            currency=localized_currency,
            lang=self.user_lang
        )
        await interaction.response.send_message(success_template, ephemeral=True)

        self.stop()


class ShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shop", aliases=["sd"])
    async def shop_command(self, ctx, subcommand: str = None, arg: str = None):
        """
        Usage:
          ^shop          -> View the shop (page 1)
          ^shop view     -> Same as above
          ^shop buy <ID> -> Attempt to buy the item with <ID>
        """
        try:
            user_collection = get_collection("users")
        except DatabaseError:
            await ctx.send("Database Error! Contact Bot admins!")
            return

        user_id = str(ctx.author.id)
        user = user_collection.find_one({"user_id": user_id})
        user_lang = user.get("lang", "CHS") if user else "CHS"

        if not subcommand or subcommand.lower() == "view":
            shop_items = load_shop()
            if not shop_items:
                _, no_items_text = get_response("shop_no_items", lang=user_lang)
                await ctx.send(no_items_text)
                return

            view = ShopView(ctx, shop_items, user_lang=user_lang)
            embed = view.create_embed()
            await ctx.send(embed=embed, view=view)
            return

        if subcommand.lower() == "buy":
            if not arg:
                _, invalid_cmd = get_response("shop_invalid_subcommand", lang=user_lang)
                await ctx.send(invalid_cmd)
                return

            try:
                shop_item_id = int(arg)
            except ValueError:
                _, invalid_cmd = get_response("shop_invalid_subcommand", lang=user_lang)
                await ctx.send(invalid_cmd)
                return

            shop_items = load_shop()
            shop_item = None
            for itm in shop_items:
                if itm["shop_item_id"] == shop_item_id:
                    shop_item = itm
                    break

            if not shop_item:
                _, not_found_msg = get_response("shop_item_not_found", shop_item_id=shop_item_id, lang=user_lang)
                await ctx.send(not_found_msg)
                return

            textmap = load_localisation(user_lang)
            localized_currency = textmap["currency_display"].get(shop_item["currency"], shop_item["currency"])
            item_name = textmap["items"].get(str(shop_item["item_id"]), f"NO_TEXT(Item#{shop_item['item_id']})")

            _, buy_prompt = get_response(
                "shop_buy_prompt",
                item_name=item_name,
                quantity=shop_item["quantity"],
                price=shop_item["price"],
                currency=localized_currency,
                lang=user_lang
            )

            view = ConfirmBuyView(ctx, user_lang, shop_item)
            await ctx.send(buy_prompt, view=view)
            return

        _, invalid_cmd = get_response("shop_invalid_subcommand", lang=user_lang)
        await ctx.send(invalid_cmd)

async def setup(bot):
    await bot.add_cog(ShopCommand(bot))
