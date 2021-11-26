import asyncio
import nextcord as discord
from nextcord.ext import commands
from utilities.utilities import TimeConverter


class mod(commands.Cog):

    """
    Moderation commands to manage the server!
    These can be used only by people with respective permissions to the commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("-" * 50)
        print(f"{self.qualified_name} loaded")

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_roles=True)
    async def unmute(self, ctx, *, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="muted")
        if role is None:
            await ctx.send("A muted role hasn't been created")
            return
        if role not in member.roles:
            return await ctx.send("The member isn't muted!")
        await member.remove_roles(role)
        await ctx.send(f"`{member}` has been unmuted succesfully!")
        await member.send(f"You have been unmuted in `{ctx.guild.name}`")

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, time: TimeConverter = None):
        role = discord.utils.get(ctx.guild.roles, name="muted")
        if role is None:
            return await ctx.send(
                "No muted role found, please make a role called `muted` and run the command again"
            )
        elif role in member.roles:
            return await ctx.send("The member is already muted")
        await member.add_roles(role)
        await ctx.send(
            (
                f"Muted `{member.display_name}` for {time} seconds"
                if time is not None
                else f"Muted `{member.display_name}`"
            )
        )
        await member.send(
            (
                f"You were muted in {ctx.guild.name}"
                if time is None
                else f"You were muted in {ctx.guild.name} for {time} seconds"
            )
        )
        if time is not None:
            await asyncio.sleep(time)
            try:
                await member.remove_roles(role)

                await member.send(
                    f"""You have been unmuted in {ctx.guild.name}
                Reason: Mute Duration expired"""
                )
            except:
                pass

    @commands.command(case_insensitive=True, description="Bans the mentioned user")
    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned from {ctx.guild.name}")

    @commands.guild_only()
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked from {ctx.guild.name}")

    @commands.command(
        case_insensitive=True,
        aliases=["clear", "clean", "c"],
        description="Purges a certain amount of messages or 5 messages if no number mentioned",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"{amount} messages purged", delete_after=5)

    @commands.command(
        case_insensitive=True,
        aliases=["announce"],
        description="Announces a message in a specified channel",
    )
    @commands.guild_only()
    @commands.bot_has_guild_permissions(administrator=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def echo(self, ctx, channel: discord.TextChannel = None, *, message):
        await channel.send(message)
        await ctx.send(f"Announced {message} in {channel}")


def setup(bot):
    bot.add_cog(mod(bot))
