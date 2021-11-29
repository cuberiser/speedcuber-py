import json
import nextcord as discord
from nextcord.ext import commands
import random
import asyncio


def rpsmsg(userchoice, author: discord.Member):
    computerchoice = random.choice(["Rock", "Paper", "Scissors"])
    user = userchoice.lower()[0]
    comp = computerchoice.lower()[0]
    if user not in ['r', 'p', 's']:
        return f"{author.mention} Invalid choice"
    if user == comp:
        return f"{author.mention} You tied with the computer by choosing {userchoice}!"
    elif (user == 'r' and comp == 'p') or (user == 'p' and comp == 's') or (user == 's' and comp == 'r'):
        return f"{author.mention} You lost! computer chose {computerchoice}"
    elif (user == 'r' and comp == 's') or (user == 'p' and comp == 'r') or (user == 's' and comp == 'p'):
        return f"{author.mention} You won by using {userchoice}!"


class rpsdropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Rock", emoji="🪨", description="Rock go bam"),
            discord.SelectOption(label="Paper", emoji="📃", description="Paper is paper"),
            discord.SelectOption(label="Scissors", emoji="✂️", description="Scissors go cut")
        ]
        super().__init__(placeholder="Select from these", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(str(rpsmsg(self.values[0], interaction.user)))        
        self.disabled = True
        self.placeholder = "This game has now ended."
        view = discord.ui.View()
        view.add_item(self)
        await interaction.message.edit(content=f"The game has ended.", view=view)


class rpsview(discord.ui.View):
    def __init__(self, ctx, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
    
    async def interaction_check(self, interaction: discord.Interaction):
        return self.ctx.author == interaction.user


class misc(commands.Cog):

    """
    Miscallaneous/Fun commands
    """

    def __init__(self, bot):
        self.bot = bot

    def iscuberiser():
        async def predicate(ctx):
            return ctx.author.id == 752020937335111801

        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print('-'*50)
        print(f"{self.qualified_name} loaded")

    
    @commands.command(
        case_insensitive=True,
        description="Guess a random number between 1 and 10 and see if you get it right!",
    )
    async def guess(self, ctx):

        m = await ctx.send("Guess a number within 15 seconds!")

        try:
            number = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.channel.id == ctx.channel.id
                and message.author == ctx.author,
            )
            random_num = random.randint(1, 10)
            if number.content.isdigit():
                number = int(number.content)
                if number == random_num:
                    await ctx.send("You guessed the right number")
                else:
                    await ctx.send(
                        f"Your guess was wrong! The random number was {random_num}"
                    )
            else:
                await ctx.send("Imagine guessing non numbers")

        except asyncio.TimeoutError:
            await m.edit(f"{ctx.author.mention} You didn't guess in time so you lost!")


    @commands.command()
    async def rps(self, ctx, option: str=False):
        if option:
            await ctx.send(rpsmsg(option, ctx.author))
            return
        view = discord.ui.View()
        drop = rpsdropdown()
        view.add_item(drop)
        await ctx.send("Choose an option", view=view)


    """@commands.command(case_insensitive=True,
    description="Play a game of rock paper scissors with the bot!")
    async def rps(self, ctx):
      comp = random.choice(ch1)
      yet = discord.Embed(title=f"{ctx.author.display_name}'s Rock Paper Scissors Game against bot: {self.bot.user.name}, click on buttons to play!", description="> Status: you haven't chosen an option yet", color=0xFFEA00)
      win = discord.Embed(title=f"{ctx.author.display_name}, You Won!", description=f"**You have won!** Bot had chosen {comp}", color=0x00FF00)
      out = discord.Embed(title=f"{ctx.author.display_name} Imagine not clicking on time, smh my head", description="**Timed out!**", color=discord.Color.red())
      lost = discord.Embed(title=f"{ctx.author.display_name}, You Lost!", description=f"**You have lost!** Bot had chosen {comp}", color=discord.Color.red())
      tie = discord.Embed(title=f"{ctx.author.display_name}, It's a tie!", description=f"**It was a tie!** Both have chosen {comp}", color=0x00FF00)
      m = await ctx.send(embed=yet, components=[[Button(style=ButtonStyle.red, label="Rock"),Button(style=ButtonStyle.blue, label="Paper"),Button(style=3, label="Scissors")]])
      def check(respons):
        return ctx.author == respons.author and respons.channel == ctx.channel

      try:
         res = await self.bot.wait_for("button_click", check=check, timeout=15)
         player = res.component.label
            
         if player==comp:
          await m.edit(embed=tie,components=[])
              
         if player=="Rock" and comp=="Paper":
          await m.edit(embed=lost,components=[])
              
         if player=="Rock" and comp=="Scissors":
          await m.edit(embed=win,components=[])
            
            
         if player=="Paper" and comp=="Rock":
          await m.edit(embed=win,components=[])
              
         if player=="Paper" and comp=="Scissors":
          await m.edit(embed=lost,components=[])
              
              
         if player=="Scissors" and comp=="Rock":
          await m.edit(embed=lost,components=[])
              
         if player=="Scissors" and comp=="Paper":
          await m.edit(embed=win,components=[])
            

      except asyncio.TimeoutError:
          await m.edit(
              embed=out,
              components=[],
          )"""


def setup(bot):
    bot.add_cog(misc(bot))
