import nextcord as discord
from nextcord.ext import commands
from utilities.utilities import read_json, write_json


class bot_customization(commands.Cog):

    """
    These commands are to customize the bot to your liking,
    these can be used by admins of servers only!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("-" * 50)
        print(f"{self.qualified_name} loaded")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        data = read_json("blacklistedusers.json")
        enabled_guilds = data["welcome_message_enabled_servers"]
        if str(member.guild.id) in enabled_guilds:
            channel = discord.utils.get(member.guild.text_channels, name="👋-welcome")
            if channel is None:
                channel = discord.utils.get(member.guild.text_channels, name="welcome")
                if channel is None:
                    channel = discord.utils.get(
                        member.guild.text_channels, name="joins"
                    )
                    if channel is None:
                        return
            joinembed = discord.Embed(
                title=f"{member.display_name} joined {member.guild.name}!",
                description=f"Welcome {member.mention} to {member.guild.name}, {member.guild.member_count}th member to join! Make sure to get your roles!",
            )
            joinembed.set_thumbnail(url=member.guild.icon_url)
            joinembed.set_image(url=member.display_avatar.url)
            await channel.send(embed=joinembed)

    @commands.command(
        aliases=["report error"], description="report an error with the bot"
    )
    async def report(self, ctx: commands.Context, *, complaint):
        report_emb = discord.Embed(
            title=f"reported by {ctx.author.name}",
            description=f"{ctx.author} reported this error",
        )
        report_emb.set_footer(
            icon_url=ctx.author.display_avatar.url,
            text=f"reported by {ctx.author}\nreporter's ID is {ctx.author.id}",
        )
        report_emb.add_field(name="error", value=f"error is:\n**{complaint}**")

        await self.bot.get_channel(865185403351203870).send(embed=report_emb)
        await ctx.reply("Your error has been reported!")

    @commands.command(
        case_insensitive=True,
        aliases=["change-prefix", "change_prefix"],
        description="Changes the prefix of the bot for the current server",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def changeprefix(self, ctx, *, new_prefix):
        await self.bot.config.upsert({"_id": ctx.guild.id, "prefix": new_prefix})
        await ctx.send(f"I have set the prefix to {new_prefix}")

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def resetprefix(self, ctx):
        await self.bot.config.unset({"_id": ctx.guild.id, "prefix": 1})
        await ctx.send("I have succesfully reset the prefix")

    @commands.command(
        description="Enables or disables the welcome message when a member joins or leaves"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle_welcome(self, ctx):
        data = read_json("blacklistedusers.json")
        if str(ctx.guild.id) not in data["welcome_message_enabled_servers"]:
            data["welcome_message_enabled_servers"].append(str(ctx.guild.id))
            write_json("blacklistedusers.json", data)
            await ctx.reply(
                "The welcome message has been enabled, make sure your server has a channel called `👋-welcome` or `welcome` or `joins"
            )
        else:
            data["welcome_message_enabled_servers"].remove(str(ctx.guild.id))
            write_json("blacklistedusers.json", data)
            await ctx.reply("The welcome message has succesfully been removed")


def setup(bot):
    bot.add_cog(bot_customization(bot))
