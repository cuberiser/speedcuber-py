import nextcord as discord
from nextcord.ext import commands


class helpDropdown(discord.ui.Select):
    def __init__(self, bot) -> None:
        options = [
            discord.SelectOption(label="mod", emoji="🔨"),
            discord.SelectOption(label="misc", emoji="🎉"),
            discord.SelectOption(label="utils", emoji="🔦"),
            discord.SelectOption(label="cubing", emoji="💠"),
            discord.SelectOption(label="bot_customization", emoji="🤖")
        ]
        super().__init__(placeholder="Choose a category", options=options)
        self.bot: commands.Bot = bot
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.values[0], color=discord.Color.random())
        text = "```\n"
        cog = self.bot.get_cog(self.values[0])
        if not cog:
            await interaction.message.edit(content="An error occured")
        else:
            for command in cog.walk_commands():
                if command.hidden:
                    continue
                text += f"{command.qualified_name}{command.signature if command.signature else ''}\n"
            text += "\n```"
            embed.description = text
            await interaction.message.edit(embed=embed)



class ownerhelp(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Loaded")

    @commands.command()
    async def ownerhelp(self, ctx, command):
        if command is None:
            embed = discord.Embed(
                title="Get some help",
                description=f"All of {self.bot.user.display_name}'s commands\nBot description-{self.bot.description}",
                color=discord.Colour.random(),
            )
            embed.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"All categories, do {ctx.command.name} [command|category] to see more info about commands or categories",
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            cogs = [c for c in self.bot.cogs.keys()]
            cogs.remove("dev")
            cogs.remove("help_command")
            if ctx.guild is None or not ctx.author.guild_permissions.manage_channels:
                cogs.remove("channels")
            if ctx.guild is None or not ctx.author.guild_permissions.administrator:
                cogs.remove("bot_customization")
            if ctx.guild is None or not ctx.author.guild_permissions.manage_messages:
                cogs.remove("mod")
            if ctx.guild is None:
                cogs.remove("utils")
            for cog in cogs:
                realcog = self.bot.get_cog(cog)

                cog_commands_1 = [command for command in realcog.walk_commands()]
                cog_commands = ""

                for cmd in cog_commands_1:
                    if cmd.hidden:
                        continue
                    elif cmd.parent is not None:
                        continue

                    cog_commands += f"{cmd.qualified_name}\n"

                embed.add_field(
                    name=cog,
                    value=f"""Category description - {realcog.description}
                Commands in the category-\n```{cog_commands}```""",
                    inline=False,
                )
            view = helpView(ctx)
            view.add_item(helpDropdown(self.bot))
            await ctx.send(embed=embed, view=view)

        else:
            cmd = self.bot.get_command(command)
            if cmd is None:
                cog = self.bot.get_cog(command)
                if not cog:
                    return await ctx.send(
                        f"Invalid command or category - `{command}`, it does not exist, make sure you got the capitalization and names exactly correct!"
                    )
                embed = discord.Embed(title=cog.qualified_name)
                coghelptext = f"**{cog.description}**\n```"
                for command in cog.walk_commands():
                    coghelptext += f"{command.qualified_name} - {command.description}\n"
                coghelptext += "\n```"
                embed.description = coghelptext
                if ctx.author.avatar is not None:
                    embed.set_thumbnail(url=(self.bot.user.avatar.url if self.bot.user.avatar is not None else ctx.author.display_avatar.url))
                await ctx.send(embed=embed)
            else:
                cmd_aliases = [alias for alias in cmd.aliases]
                embed = discord.Embed(title=cmd.qualified_name)
                helptext = ""
                helptext += f"**{cmd.description}**\n"
                helptext += f"Format: {cmd.qualified_name} {cmd.signature if cmd.signature is not None else ''}\n"
                if len(cmd.aliases) != 0:
                    cmd_aliases.append(cmd.qualified_name)
                    helptext += "Aliases - " + "|".join(cmd_aliases) + "\n"
                embed.description = helptext
                embed.set_footer(
                    text=f"<> - Required arguments | [] - Optional Arguments | Viewing command {cmd.name}"
                )
                embed.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(ownerhelp(bot))
