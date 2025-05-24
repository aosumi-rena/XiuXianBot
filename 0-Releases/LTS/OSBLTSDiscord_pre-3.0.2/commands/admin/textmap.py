from discord.ext import commands
import discord
import os
import json

# Admin IDs
admin_ids = [1234567890]

class TextmapIndexView(discord.ui.View):
    def __init__(self, index_lines, lang, per_page=10):
        super().__init__(timeout=120)
        self.index_lines = index_lines
        self.lang = lang.upper()
        self.per_page = per_page
        self.page = 1
        self.total_pages = (len(self.index_lines) + per_page - 1) // per_page
        self.update_button_states()

    def update_button_states(self):
        for child in self.children:
            if child.custom_id == "prev":
                child.disabled = (self.page <= 1)
            elif child.custom_id == "next":
                child.disabled = (self.page >= self.total_pages)

    def get_page_lines(self):
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.index_lines[start:end]

    def create_embed(self):
        page_lines = self.get_page_lines()
        description = "\n".join(page_lines) if page_lines else "No entries found."
        embed = discord.Embed(
            title=f"Textmap Index for {self.lang} (Page {self.page}/{self.total_pages})",
            description=description,
            color=discord.Color.gold()
        )
        return embed

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary, custom_id="prev", row=0)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("[DEBUG]admin/textmap.py: TM indexing page - Prev button pressed.")  # Debug
        if self.page > 1:
            self.page -= 1
            self.update_button_states()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()  # No change

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary, custom_id="next", row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("[DEBUG]admin/textmap.py: TM indexing page - Next button pressed.")  # Debug
        if self.page < self.total_pages:
            self.page += 1
            self.update_button_states()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()  # No change

class AdminTextmapCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, user_id):
        """Check if a user is an admin."""
        return user_id in admin_ids

    def load_textmap(self, lang):
        """Load the specified textmap."""
        try:
            filepath = os.path.join('textmaps', f'{lang}.json')
            with open(filepath, encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Textmap for '{lang}' not found.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    @commands.command(name='admin:textmap', aliases=['a:text', 'a:tm'])
    async def admin_textmap(self, ctx, lang: str = None, textmap_codename: str = None):
        """
        Retrieve details of a specific textmap entry, or show an index if no codename is provided.
        If no language is provided, default to CHS.
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("You are not authorized to use this command.")
            return

        # Default language to CHS if not provided.
        if not lang or lang.lower() == "none":
            lang = "CHS"
        else:
            lang = lang.upper()
            if lang not in ['EN', 'CHS', 'CHT']:
                await ctx.send("Invalid language. Use one of: EN, CHS, CHT.")
                return

        try:
            textmap_data = self.load_textmap(lang)
            responses = textmap_data.get('responses', {})

            if not textmap_codename or textmap_codename.lower() == "none":
                # Build an index: list each key and whether it exists in both CHS and EN.
                en_responses = {}
                try:
                    en_textmap = self.load_textmap("EN")
                    en_responses = en_textmap.get("responses", {})
                except Exception:
                    pass  # If EN textmap isn't available, continue

                index_lines = []
                sorted_keys = sorted(responses.keys())
                for i, key in enumerate(sorted_keys, start=1):
                    available_in_en = "✅" if key in en_responses else "❌"
                    # For CHS, assume available.
                    available_in_chs = "✅"
                    index_lines.append(f"{i}. **{key}** - CHS: {available_in_chs} | EN: {available_in_en}")
                
                view = TextmapIndexView(index_lines, lang, per_page=10)
                embed = view.create_embed()
                await ctx.send(embed=embed, view=view)
                return

            entry = responses.get(textmap_codename)
            if not entry:
                await ctx.send(f"No entry found for codename '{textmap_codename}' in {lang}.")
                return

            description = entry.get('description', 'No description provided.')
            type_ = entry.get('type', 'Unknown type.')
            text = entry.get('text', 'No text provided.')
            response_message = (
                f"- **Description**: `{description}`\n"
                f"- **Type**: `{type_}`\n"
                f"- **Text**:\n```\n{text}\n```"
            )
            await ctx.send(response_message)

        except Exception as e:
            await ctx.send(f"**ERROR**: {e}")
        except FileNotFoundError:
            await ctx.send(f"Textmap for '{lang}' not found.")
        except json.JSONDecodeError as e:
            await ctx.send(f"Invalid JSON format: {e}")

async def setup(bot):
    await bot.add_cog(AdminTextmapCommand(bot))
