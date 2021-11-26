import nextcord as discord
from nextcord.ext import commands
import random
import pycuber as pc
from main import guild_ids


class cubing(commands.Cog):

    """
    Cubing related commands!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('-'*50)
        print(f"{self.qualified_name} loaded")
    

    @commands.group(case_insensitive=True)
    async def cube(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "https://i.pinimg.com/originals/0a/7d/08/0a7d08532815fdd8a402860e3150d48d.png this is a cube"
            )

    @commands.command(name='invite')
    async def lol(self, ctx):
        await ctx.reply(
            """here is the link to the bot's invite! -
        https://discord.com/api/oauth2/authorize?client_id=863702962194743307&permissions=2146958847&scope=bot%20applications.commands"""
        )

    @cube.command(case_insensitive=True)
    async def riser(self, ctx):
        await ctx.send("https://youtube.com/cuberiser Subscribe!")

    @cube.group(case_insensitive=True)
    async def solve(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "I can't help you solve a cube go watch a tutorial\nhttps://www.youtube.com/results?search_query=how+to+solve+a+rubik%27s+cube"
            )

    @solve.command(case_insensitive=True)
    async def hero(self, ctx):
        emb = discord.Embed(
            title="Cube Solve Hero's YouTube channel",
            description="[Cube Solve Hero's YouTube channel](https://www.youtube.com/c/CubeSolveHero)",
        )

        await ctx.send(embed=emb)

    @commands.command(aliases=["rs3", "rs3m", "rs32020"], case_insensitive=True)
    async def rs3m2020(self, ctx):
        await ctx.send(
            "Here is Cube Riser's review of it!:\nhttps://www.youtube.com/watch?v=8VcOBOQXoaw"
        )

    @commands.command(
        aliases=["3", "scramble", "cube3", "s3", "scramble3"],
        description="gets you a 3x3 scramble with a preview",
        case_insensitive=True,
    )
    async def scram(self, ctx):
        def Scramble():
            moves = ["U", "D", "F", "B", "R", "L"]
            dir = ["", "'", "2"]
            slen = random.randint(25, 28)

            def gen_scramble():
                s = validate(
                    [[random.choice(moves), random.choice(dir)] for x in range(slen)]
                )
                return (
                    "".join(str(s[x][0]) + str(s[x][1]) + " " for x in range(len(s))),
                    "[" + str(slen) + "]",
                )

            def validate(ar):
                for x in range(1, len(ar)):
                    while ar[x][0] == ar[x - 1][0]:
                        ar[x][0] = random.choice(moves)
                for x in range(2, len(ar)):
                    while ar[x][0] == ar[x - 2][0] or ar[x][0] == ar[x - 1][0]:
                        ar[x][0] = random.choice(moves)
                return ar

            return gen_scramble()

        scramble = Scramble()

        mycube = pc.Cube()
        mycube(scramble[0])

        mycube = str(mycube)
        mycube = mycube.replace("[o]", ":red_square:")
        mycube = mycube.replace("[r]", ":orange_square:")
        mycube = mycube.replace("[y]", ":white_large_square:")
        mycube = mycube.replace("[b]", ":blue_square:")
        mycube = mycube.replace("[g]", ":green_square:")
        mycube = mycube.replace("[w]", ":yellow_square:")
        mycube = mycube.replace("   ", ":black_large_square:")
        embed = discord.Embed(
            title=scramble[0] + scramble[1],
            url="",
            description=mycube,
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command(case_insensitive=True, description="J Perm's YouTube channel")
    async def jperm(self, ctx):

        emb = discord.Embed(
            title="JPerm's YouTube channel",
            description="[J Perm's YouTube channel](https://youtube.com/jperm)",
        )

        await ctx.send(embed=emb)

    @commands.command(case_insensitive=True)
    async def cubehead(self, ctx):

        emb = discord.Embed(
            title="CubeHead's YouTube channel",
            description="[Cube Head's YouTube channel](https://youtube.com/cubehead)",
        )

        await ctx.send(embed=emb)

    @commands.command(case_insensitive=True)
    async def cubingencoded(self, ctx):
        await ctx.send("here is his channel-\nhttps://youtube.com/cubingencoded")


def setup(bot):
    bot.add_cog(cubing(bot))
