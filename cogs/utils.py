import datetime
import nextcord as discord
from nextcord.ext import commands
from main import guild_ids
import aiohttp
import io
import humanize as hmz

class utils(commands.Cog):

    """
    Utility commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("-" * 50)
        print(f"{self.qualified_name} loaded")

    @commands.command(
        description="Gets the info about the server",
        case_insensitive=True,
        aliases=["si"],
    )
    @commands.guild_only()  # so the command can be used only in servers
    async def serverinfo(self, ctx: commands.Context):
        role_count = len(ctx.guild.roles)
        role_list = [
            role.mention for role in ctx.guild.roles if not role.is_bot_managed()
        ]
        serverinfoemb = discord.Embed(
            title=f"{ctx.guild.name}'s info", color=ctx.author.color
        )
        serverinfoemb.set_footer(
            icon_url=ctx.author.avatar.url, text=f"Requested by {ctx.author}"
        )
        serverinfoemb.add_field(name="Name", value=f"{ctx.guild.name}", inline=False)
        serverinfoemb.add_field(
            name="Owner", value=f"{ctx.guild.owner.mention}", inline=False
        )
        serverinfoemb.add_field(
            name="Membercount", value=ctx.guild.member_count, inline=False
        )
        serverinfoemb.add_field(
            name="verification level",
            value=str(ctx.guild.verification_level),
            inline=False,
        )
        serverinfoemb.add_field(name="Role count", value=str(role_count), inline=False)
        serverinfoemb.add_field(
            name="Highest role",
            value=f"Highest-\n{ctx.guild.roles[-1].mention}",
            inline=False,
        )
        serverinfoemb.add_field(
            name="Created at",
            value=ctx.guild.created_at.strftime("%d-%m-%y %X"),
            inline=False,
        )
        serverinfoemb.add_field(name="roles", value=", ".join(role_list), inline=False)

        await ctx.send(embed=serverinfoemb)

    @commands.command(
        aliases=["pfp", "logo"],
        case_insensitive=True,
        description="Gets a member's avatar",
    )
    @commands.guild_only()  # so the command can be used only in servers
    async def avatar(self, ctx, *, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if member.avatar is None:
            await ctx.send("The member doesn't have an avatar and uses the default")
            return

        pfp_embed = discord.Embed(title=f"{member.name}'s avatar")
        pfp_embed.set_image(url=member.avatar.url)
        pfp_embed.set_footer(
            icon_url=ctx.author.avatar.url, text=f"Requested by {ctx.author.name}"
        )

        await ctx.send(embed=pfp_embed)

    @commands.command(description="gets the latency of the bot", case_insensitive=True)
    async def ping(self, ctx):
        await ctx.send(
            f"Pong! {self.bot.user.mention}'s ping is {(self.bot.latency*1000):.2f} ms"
        )

    @commands.command(
        aliases=["mc", "members", "member-count"],
        case_insensitive=True,
        description="Show the amount of members",
    )
    @commands.guild_only()
    async def membercount(self, ctx):
        await ctx.send(f"{ctx.guild.name} has {ctx.guild.member_count} members!")

    @commands.command(
        aliases=["servers"],
        case_insensitive=True,
        description="Shows what all servers the bot is in",
    )
    @commands.dm_only()
    async def serverlist(self, ctx, limit: int = None):
        if limit is None:
            limit = 15
        servers = ""
        async for guild in self.bot.fetch_guilds(limit=limit):
            servers += f"\n{guild}"
        server_emb = discord.Embed(
            title=f"{self.bot.user}'s servers!", description=servers
        )
        await ctx.send(embed=server_emb)

    @commands.command()
    async def version(self, ctx):
        await ctx.send(f"My version is {self.bot.version}")

    @commands.command(
        description="Performs a google search",
        aliases=["google-search", "google_search"],
    )
    async def search(self, ctx, *query):
        emb = discord.Embed(
            title=f"{ctx.author}'s search",
            description="[Click here to view](https://google.com/search?q="
            + "+".join(query)
            + ")",
            color=discord.Colour.random(),
        )
        await ctx.send(embed=emb)

    @commands.command(aliases=["calculator"])
    async def calc(self, ctx: commands.Context, *, question: str):
        question = (((question.lower()).replace("x", "*")).replace("^", "**")).replace(
            "÷", "/"
        )
        for char in question:
            if char.isalpha():
                raise commands.BadArgument(
                    "Bad argument, an expression mustn't contain alphabets"
                )

        result = float(eval(question))
        em = discord.Embed(
            title="Calculation done succesfully", description=f"Result: {result}"
        )
        em.set_author(
            icon_url=ctx.author.display_avatar.url,
            url="https://www.youtube.com/watch?v=xvFZjo5PgG0",
            name=f"{ctx.author}",
        )
        await ctx.send(embed=em)

    @commands.command()
    async def userinfo(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        user_roles = [role.mention for role in user.roles]
        emb = discord.Embed(title=f"{user}'s info", color=user.color)
        emb.add_field(name="Name", value=user.name, inline=False)
        emb.add_field(name="Nickname", value=user.display_name, inline=False)
        emb.add_field(name="Discriminator", value=user.discriminator, inline=False)
        emb.add_field(name="ID", value=str(user.id), inline=False)
        emb.add_field(
            name="Joined discord at",
            value=user.created_at.strftime("%d-%m-%y"),
            inline=False,
        )
        emb.add_field(
            name="Joined server at",
            value=user.joined_at.strftime("%d-%m-%y"),
            inline=False,
        )
        emb.add_field(name="Mention", value=user.mention, inline=False)
        emb.add_field(name="Highest role", value=(user.roles[-1]).mention)
        emb.set_thumbnail(url=user.display_avatar.url)
        await ctx.send(embed=emb)

    @commands.command()
    async def find_emoji(self, ctx, *, emoji_name):
        for emoji in ctx.guild.emojis:
            if emoji.name == emoji_name:
                await ctx.send(emoji)
                break

        else:
            await ctx.send("Emoji not found")

    @commands.command()
    @commands.has_guild_permissions(manage_emojis=True)
    async def steal(self, ctx: commands.Context, link: str, name):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(link) as r:
                if r.status in range(200, 299):
                    try:
                        bytevalue = (io.BytesIO(await r.read())).getvalue()
                        emoji = await ctx.guild.create_custom_emoji(
                            name=name, image=bytevalue
                        )
                        await ctx.send(f"Emoji added succesfully {emoji}")
                    except discord.HTTPException:
                        await ctx.send("File was unfortunately too large!")
                else:
                    await ctx.send("Failed while getting file!")
    
    @commands.command()
    async def uptime(self, ctx):
        now = datetime.datetime.now()
        so: datetime.datetime = self.bot.started_on
        total_seconds = (now - so).total_seconds()
        time = hmz.naturaltime(total_seconds)
        await ctx.send(f"I started {time}.")


def setup(bot):
    bot.add_cog(utils(bot))
