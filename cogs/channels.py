import nextcord as discord
from nextcord.ext import commands


def channel_perms():
    async def predicate(ctx):
        return (
            ctx.guild is not None and ctx.author.guild_permissions.manage_channels
        )

    return commands.check(predicate)


class channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
   
    @commands.Cog.listener()
    async def on_ready(self):
        print('-'*50)
        print(f"{self.qualified_name} loaded")

    @commands.command(
        aliases=["createchannel", "create-channel", "create_channel"],
        case_insensitive=True,
        description="Creates a text channel with specified name",
    )
    @channel_perms()
    async def create(self, ctx, *, name):
        channel = await ctx.guild.create_text_channel(name=name)
        await ctx.send(f"I have created {channel.mention}")
        await channel.send(
            f"{channel.mention} created by {ctx.author} aka `{ctx.author.display_name}`"
        )

    @create.error
    async def createchannelerror(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have permissions to use this command")
        else:
            await ctx.send(f"{error}")

    @commands.command(
        aliases=["delete-channel", "delete_channel"],
        case_insensitive=True,
        description="Deletes the specified or current text channel if nothing is specified",
    )
    @channel_perms()
    async def delete(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        msg = await ctx.send(f"deleting {channel.mention}")
        await channel.delete()
        try:
            await msg.edit(f"Deleted {channel.name}")
        except:
            pass

    @delete.error
    async def delchanerror(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You are missing permissions to use the command!")
        else:
            await ctx.send(f"{error}")

    @commands.command(
        case_insensitive=True,
        description="Sets a desired slowmode for the current channel",
    )
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def slowmode(self, ctx, amount: int, *, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        if amount > 21600:
            return await ctx.send(
                "The slowmode can't be more than 6 hours which is 21600 seconds!"
            )
        await channel.edit(slowmode_delay=amount)
        await ctx.send(f"Set the slowmode for {channel.mention} to {amount} seconds!")

    @slowmode.error
    async def slerror(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command can't be used in DMs!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please put in an amount for the slowmode in seconds!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You are missing permissions to use the command!")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Please give the bot permissions to use the command!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(
                "Please put in a actual whole number, and not letters or decimal numbers!"
            )
        else:
            await ctx.send(f"{error}")

    @commands.command(
        case_insensitive=True, description="Locks the specified or current channel"
    )
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"I have locked {channel}")

    @commands.command(
        case_insensitive=True, description="Unlocks the specified or current channel"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f"I have unlocked {channel}")

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("DMs can't be locked!")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Bot missing manage channels perms")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the manage channels permission")
        else:
            await ctx.send(
                f"An error occured, report it with the ,report command if it needs to be fixed\nerror descripition:\n**{error}**"
            )

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("DMs aren't locked to unlock it.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Bot missing manage channels perms")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the manage channels permission")
        else:
            await ctx.send(
                f"An unexpected error occured, report it with the ,report command if it needs to be fixed\nerror descripition:\n**{error}**"
            )


def setup(bot):
    bot.add_cog(channels(bot))
