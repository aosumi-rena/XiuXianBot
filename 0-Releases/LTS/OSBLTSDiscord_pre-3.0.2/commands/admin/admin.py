import discord
from discord.ext import commands
from utils.database import get_collection, DatabaseError

# Admin IDs
admin_ids = [1234567890]

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, user_id):
        return user_id in admin_ids

    @commands.command(name='admin:exp', aliases=['a:exp'])
    async def admin_exp(self, ctx, user: discord.Member, action: str, value: str):
        #exp
        await self.modify_user_field(ctx, user, "exp", action, value)

    @commands.command(name='admin:copper', aliases=['a:copper'])
    async def admin_copper(self, ctx, user: discord.Member, action: str, value: str):
        #copper
        await self.modify_user_field(ctx, user, "copper", action, value)

    @commands.command(name='admin:gold', aliases=['a:gold'])
    async def admin_gold(self, ctx, user: discord.Member, action: str, value: str):
        #gold
        await self.modify_user_field(ctx, user, "gold", action, value)

    @commands.command(name='admin:stage', aliases=['a:stage'])
    async def admin_stage(self, ctx, user: discord.Member, action: str, value: str):
        #stage
        await self.modify_user_field(ctx, user, "rank", action, value)

    async def modify_user_field(self, ctx, user: discord.Member, field: str, action: str, value: str):
        if not self.is_admin(ctx.author.id):
            await ctx.send("You are not authorized to use this command.")
            return
        try:
            user_collection = get_collection('users')
            target_user = user_collection.find_one({"user_id": str(user.id)})

            if not target_user:
                await ctx.send(f"User {user.mention} does not exist in the database.")
                return

            in_game_username = target_user.get("in_game_username", user.display_name)
        except DatabaseError:
            await ctx.send(content="Database Error! Contact Bot admins!")

        try:
            value = int(value)
        except ValueError:
            await ctx.send(f"Failed to modify {in_game_username}'s {field}.\nReason: Invalid value '{value}'.")
            return

        if action.lower() == "set":
            user_collection.update_one({"user_id": str(user.id)}, {"$set": {field: value}})
            await ctx.send(f"Successfully set {in_game_username}'s {field} to {value}.")
        elif action.lower() == "add":
            user_collection.update_one({"user_id": str(user.id)}, {"$inc": {field: value}})
            await ctx.send(f"Successfully added {value} to {in_game_username}'s {field}.")
        elif action.lower() == "minus":
            user_collection.update_one({"user_id": str(user.id)}, {"$inc": {field: -value}})
            await ctx.send(f"Successfully subtracted {value} from {in_game_username}'s {field}.")
        else:
            await ctx.send(f"Invalid action '{action}'. Use 'set', 'add', or 'minus'.")

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))