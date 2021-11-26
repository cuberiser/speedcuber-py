import nextcord as discord
from nextcord.ext import commands
from utilities.utilities import read_json, statusconverter
import json


class dev(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('-'*50)
        print(f"{self.qualified_name} loaded")
    
    @commands.command(aliases=["blacklistuser"], description="No")
    @commands.is_owner()
    async def blacklist(self, ctx, member: discord.Member):
        self.bot.blacklisted_users.append(member.id)
        d = await self.bot.config.find("blacklisted_users")
        if d is None:
            d = {"_id": "blacklisted_users", "users": []}
        (d["users"]).append(member.id)
        await self.bot.config.upsert({"_id":"blacklisted_users", "users": d["users"]})

        await ctx.send(f"I have added {member.mention} to the blacklisted users")

    @commands.command(
        aliases=["unblacklistuser"], case_insensitive=True, description="No"
    )
    @commands.is_owner()
    async def unblacklist(self, ctx, member: discord.Member):
        if member.id not in self.bot.blacklisted_users:
            return await ctx.send("The user was never blacklisted.")
        self.bot.blacklisted_users.remove(member.id)
        d = await self.bot.config.find("blacklisted_users")
        if d is None:
            return await ctx.send("There are no blacklisted users.")
        (d["users"]).remove(member.id)
        await self.bot.config.upsert({"_id":"blacklisted_users", "users": d["users"]})

        await ctx.send(f"I have unblacklisted {member}")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog):
        self.bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"Successfully loaded {cog}")
        print(f"loaded {cog}")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog):
        self.bot.unload_extension(f"cogs.{cog}")
        await ctx.send(f"Successfully unloaded {cog}")
        print(f"unloaded {cog}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, cog):
        self.bot.reload_extension(f"cogs.{cog}")
        await ctx.send(f"Successfully reloaded {cog}")
        print(f"reloaded {cog}")

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            return await ctx.send("You are not the owner lol")
        await ctx.reply(f"{error}")

    @unload.error
    async def unload_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            return await ctx.send("You are not the owner")
        await ctx.message.reply(f"{error}")

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            return await ctx.send("You are not the owner of the bot lol")
        await ctx.message.reply("There was an error while reloading the cog")
        await ctx.send(f"{error}")

    @commands.command(aliases=["close"])
    @commands.is_owner()
    async def logout(self, ctx):
        await ctx.send(f"Logging out as {self.bot.user}")
        await self.bot.close()

    @logout.error
    async def logout_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("You aren't the owner <:NiceTry:846603604713537546>")
        else:
            await ctx.send(error)
    
    @commands.command()
    @commands.is_owner()
    async def toggle(self, ctx, *, command):
        command = self.bot.get_command(command)
        if command is None:
            await ctx.send("This command wasn't found")
            return
        if command == ctx.command:
            await ctx.send("You can't toggle this command as it's the command that allows you to toggle.")
            return
        command.enabled = not command.enabled
        ternary = "enabled" if command.enabled else "disabled"
        await ctx.send(f"I have {ternary} {command.qualified_name}.")
    
    @commands.command()
    @commands.is_owner()
    async def changestatus(self, ctx, status: statusconverter, statustype: str, *, message: str):
        allowedstatuses = ['playing', 'watching', 'listening']
        statustype = statustype.lower()
        if statustype not in allowedstatuses:
            return await ctx.send("Invalid status type")
        if statustype == "playing":
            await self.bot.change_presence(activity=discord.Streaming(name=message, url="https://youtube.com/cuberiser"), status=status)
        elif statustype == "watching":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=message), status=status)
        elif statustype == "listening":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=message), status=status)
        elif statustype == "competing":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=message), status=status)
        else:
            await ctx.send("An error occured while changing the presence")
        await ctx.send("I have changed my status to The one you specified.")


def setup(bot):
    bot.add_cog(dev(bot))
