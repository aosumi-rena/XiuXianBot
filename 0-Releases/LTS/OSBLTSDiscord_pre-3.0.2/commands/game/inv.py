import discord
from discord.ext import commands
from discord.ui import Button, View
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation


class InventoryView(View):
    def __init__(self, user_id, items, copper, gold, user_lang, page=1, max_per_page=5):
        super().__init__()
        self.user_id = user_id
        self.items = items
        self.copper = copper
        self.gold = gold
        self.user_lang = user_lang
        self.page = page
        self.max_per_page = max_per_page
        self.total_pages = (len(items) + max_per_page - 1) // max_per_page
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        if self.page > 1:
            self.add_item(Button(label="◀️", style=discord.ButtonStyle.primary, custom_id="prev"))
        if self.page < self.total_pages:
            self.add_item(Button(label="▶️", style=discord.ButtonStyle.primary, custom_id="next"))

    async def interaction_check(self, interaction: discord.Interaction):
        return str(interaction.user.id) == self.user_id

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
        start = (self.page - 1) * self.max_per_page
        end = start + self.max_per_page
        page_items = self.items[start:end]

        textmap = load_localisation(self.user_lang)

        currency_desc = get_response(
            "currency_description", 
            copper=self.copper, 
            gold=self.gold, 
            lang=self.user_lang
        )[1]

        items_desc = get_response(
            "items_description", 
            items_section="{items_section}", 
            lang=self.user_lang
        )[1]

        if page_items:
            item_lines = []
            for itm in page_items:
                item_name = textmap["items"].get(str(itm["item"]), f"NO_TEXT!")

                if "level" in itm:
                    line = f"- {item_name} (Lv.{itm['level']})"
                else:
                    quantity = itm.get("quantity", 1)
                    line = f"- {item_name}\***{quantity}**"

                item_lines.append(line)

            item_section = "\n".join(item_lines)
        else:
            item_section = get_response("no_items", lang=self.user_lang)[1]

        description = f"{currency_desc}\n\n{items_desc.format(items_section=item_section)}"
        embed = discord.Embed(
            title=f"Inventory",
            description=description,
            color=0x00ff00
        )
        embed.set_footer(text=f"Page {self.page} of {self.total_pages}")
        return embed


class InventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="inv", aliases=["item", "wp"])
    async def inventory(self, ctx):
        """Displays the user's inventory."""
        user_id = str(ctx.author.id)
        try:
            user_collection = get_collection("users")
            items_collection = get_collection("items")
            user = user_collection.find_one({"user_id": user_id})
            if not user:
                response_type, text = get_response("no_account", user=ctx.author.mention, lang="CHS")
                await ctx.send(text)
                return

            user_lang = user.get("lang", "CHS")
            user_ingame_name = user.get("in_game_username", ctx.author.display_name)
            copper = user.get("copper", 0)
            gold = user.get("gold", 0)

            user_items = list(items_collection.find({"owner": int(user_id)}))

            view = InventoryView(
                user_id=user_id,
                items=user_items,
                copper=copper,
                gold=gold,
                user_lang=user_lang
            )

            embed = view.create_embed()
            await ctx.send(embed=embed, view=view)
        except DatabaseError as e:
            await ctx.send(f"**Database Error:** {e}\nContact Bot Admin!")


async def setup(bot):
    await bot.add_cog(InventoryCommand(bot))
