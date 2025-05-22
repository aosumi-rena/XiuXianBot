import discord
from discord.ext import commands
from discord.ui import Button, View
from utils.database import get_collection, DatabaseError
from utils.localisations import get_response, load_localisation

# Admin IDs
admin_ids = [1234567890]

class AdminInventoryView(View):
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

        response_type, currency_desc = get_response(
            "currency_description",
            copper=self.copper,
            gold=self.gold,
            lang=self.user_lang
        )
        
        response_type, items_desc_template = get_response(
            "items_description",
            items_section="{items_section}",
            lang=self.user_lang
        )

        if page_items:
            item_lines = []
            for itm in page_items:
                item_name = textmap["items"].get(str(itm["item"]), f"NO_TEXT!")

                if "level" in itm:
                    line = f"- {item_name} (Lv.{itm['level']})"
                else:
                    qty = itm.get("quantity", 1)
                    line = f"- {item_name}\***{qty}**"

                item_lines.append(line)

            item_section = "\n".join(item_lines)
        else:
            response_type, item_section = get_response("no_items", lang=self.user_lang)

        final_items_desc = items_desc_template.format(items_section=item_section)
        description = f"{currency_desc}\n\n{final_items_desc}"

        embed = discord.Embed(
            title="Admin View: Inventory",
            description=description,
            color=0x00ff00
        )
        embed.set_footer(text=f"Page {self.page} of {self.total_pages}")
        return embed


class AdminInventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, user_id):
        return user_id in admin_ids

    @commands.command(name='admin:inv', aliases=['a:inv'])
    async def admin_inv(self, ctx, user_id: str):
        if not self.is_admin(ctx.author.id):
            await ctx.send("You are not authorized to use this command.")
            return

        try:
            user_collection = get_collection("users")
            items_collection = get_collection("items")

            user = user_collection.find_one({"user_id": user_id})
            if not user:
                await ctx.send(f"No user found with ID: {user_id}.")
                return

            user_lang = user.get("lang", "CHS")
            user_ingame_name = user.get("in_game_username", "Unknown")
            copper = user.get("copper", 0)
            gold = user.get("gold", 0)

            user_items = list(items_collection.find({"owner": int(user_id)}))

            view = AdminInventoryView(
                user_id=user_id,
                items=user_items,
                copper=copper,
                gold=gold,
                user_lang=user_lang
            )

            embed = view.create_embed()
            await ctx.send(embed=embed, view=view)

        except DatabaseError as e:
            await ctx.send(f"**Database Error:** {e}")


async def setup(bot):
    await bot.add_cog(AdminInventoryCommand(bot))
