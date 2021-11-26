# Standard libs
import datetime
import json
import io
import contextlib
import textwrap
import os
import random
import difflib
import logging

# External libs
import nextcord as discord
from nextcord.ext import commands  # , tasks
from traceback import format_exception
from itertools import cycle
import humanize as hmz
from fileops import read_json

# Database libs
from utilities.mongo import Document
from utilities.utilities import clean_code  # , read_json, write_json
import motor.motor_asyncio

blacklisted_users = []


async def get_prefix(bot, message):
    """
    Gets the bot's prefix from our database or returns default
    """
    if message.guild is None:
        return commands.when_mentioned_or(str(bot.default_prefix))(bot, message)

    try:
        data = await bot.config.find(message.guild.id)

        if not data or "prefix" not in data:
            return commands.when_mentioned_or(str(bot.default_prefix))(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except Exception:
        return commands.when_mentioned_or(str(bot.default_prefix))(bot, message)


logging.basicConfig(level=logging.INFO)
default_prefix = ","

# defining the bot
bot = commands.Bot(
    command_prefix=get_prefix,
    intents=discord.Intents().all(),
    description="A very cool cubing bot",
    help_command=None,
)

# defining a version for the bot, scuffed version of version control
bot.version = "Pre-release 0.0.2"

bot.default_prefix = default_prefix

bot.config_url = read_json("config.json")["mongo"]


# making a custom decorator for commands that can be used only by me
def iscuberiser():
    async def predicate(ctx):
        return ctx.author.id == 752020937335111801

    return commands.check(predicate)


# making people for the eval command perms and a decorator so that only they can use it
evalperms = [752020937335111801]


def eval_perms():
    async def predicate(ctx):
        return ctx.author.id in evalperms

    return commands.check(predicate)


number_of_guilds = len(bot.guilds)

statuses = cycle(
    [
        f"with a Rubik's Cube",
        f"with a Rubik's Cube | {bot.default_prefix}help",
        f"In {number_of_guilds}",
    ]
)


"""
@tasks.loop(seconds=60)
async def ch_pr():
    await bot.change_presence(activity=discord.Game(name=next(statuses)),
    status=discord.Status.invisible)
"""

guild_ids = []


# when the bot is ready, it tells you(And does a lot more)
@bot.event
async def on_ready():
    bot.started_on = datetime.datetime.now()
    print("-" * 50)
    print(f"Logged in as {bot.user} with version {bot.version}")
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.config_url))
    bot.db = bot.mongo["cubingbot"]
    bot.config = Document(bot.db, "config")
    print("-" * 50)
    print("db initted")
    await bot.change_presence(
        status=discord.Status.idle, activity=discord.Game(name="amogus")
    )
    bot.blacklisted_users = await bot.config.find("blacklisted_users")
    if bot.blacklisted_users is None:
        await bot.config.upsert({"_id": "blacklisted_users", "users": []})
        bot.blacklisted_users = []
    for document in await bot.config.get_all():
        print(document)

    async for guild in bot.fetch_guilds():
        guild_ids.append(guild.id)

    logging.info("Bot has come online")


# Handles command errors
@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.NotOwner):
        pass
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Missing permissions - " + ", ".join(error.missing_permissions))
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing argument(s) - " + ", ".join(error.args))
        return
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bad argument(s) - " + ", ".join(error.args))
        return
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"You are on cooldown for this command! Please try again in {hmz.naturaltime(error.retry_after, future=True)}"
        )
        return
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send(f"This command can only be used in servers")
        return
    elif isinstance(error, commands.CommandNotFound):
        cmd: str = ctx.invoked_with
        cmds: list[str] = [command.name for command in bot.commands]
        matches = difflib.get_close_matches(cmd, cmds)
        emb = discord.Embed(title="Invalid command error")
        if len(matches) > 0:
            emb.description = (
                f"Invalid command - `{cmd}`\nMaybe you meant `{matches[0]}`"
            )
        else:
            emb.description = f"Invalid command - {cmd}\nRun the help command to get all the commands to run!"
        await ctx.send(embed=emb)
        return
    elif isinstance(error, commands.CheckFailure):
        pass
    elif isinstance(error, commands.PrivateMessageOnly):
        await ctx.send("This command can be used only in DMs")
        return
    elif isinstance(error, discord.HTTPException):
        pass
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("This command is disabled")
        return
    else:
        print(error)
    logging.warning(str(error))


# sends a message when bot joins a server
@bot.event
async def on_guild_join(guild):
    await bot.get_channel(865185403351203870).send(f"{bot.user} joined {guild.name}!")


# Checks for messages, and what to do with them
@bot.event
async def on_message(message: discord.Message):
    # if a bot is sending a message, don't process other things for it
    if message.author.bot:
        return

    # Make sure blacklisted users don't use the bot
    if message.author.id in bot.blacklisted_users:
        return

    # waving to people when hi or hello is their message
    if message.content == "hi" or message.content == "hello":
        await message.add_reaction("👋")

    # if someone pings the bot, it responds with it's prefix
    if message.content.startswith(f"<@!{bot.user.id}>") and (
        "prefix" in message.content or len(message.content) == len(f"<@!{bot.user.id}>")
    ):

        if message.guild is None:
            prefix = "nothing in DMs"
        else:
            try:
                prefixes = bot.config.find(message.guild.id)
                if not prefixes or "prefix" not in prefixes:
                    prefix: str = bot.default_prefix
                else:
                    prefix: str = prefixes[message.guild.id]
            except Exception:
                prefix = bot.default_prefix
        await message.channel.send(
            f"The prefix of the bot is '**{prefix}**'\nLooking to change the prefix? Use the `{prefix}changeprefix` command instead",
            delete_after=10,
        )

    await bot.process_commands(message)


# Command for evaluating/executing code
@bot.command(name="eval", aliases=["exec"], description="evaluates your code")
@eval_perms()
async def eval_(ctx: commands.Context, *, code: str):
    code = clean_code(code)

    local_variables = {
        "discord": discord,
        "commands": commands,
        "bot": bot,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message,
        "random": random,
        "os": os,
        "json": json,
        "iscuberiser": iscuberiser,
        "eval_perms": eval_perms,
        "evalperms": evalperms,
    }

    stdout = io.StringIO()

    with contextlib.redirect_stdout(stdout):
        try:
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}",
                local_variables,
            )

            rv = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {rv}\n"
        except Exception as e:
            result = "\n".join(format_exception(type(e), e, e.__traceback__))

    if len(result) > 2000:
        full = result[:]
        result = result[:+1900]
        result += "[SHORTENED]"
        print(full)
    await ctx.send(f"```py\n{result}\n```")


# loads the bot's cogs!
for cog in os.listdir("cogs"):
    if cog.endswith(".py") and not cog.startswith("_"):
        bot.load_extension(f"cogs.{cog[:-3]}")

# runs the bot
if __name__ == "__main__":
    token = read_json("config.json")["token"]
    bot.run("ODYzNzAyOTYyMTk0NzQzMzA3.YOqwEQ.awFhCnINWfDYYANfQGflQ-AFMpg")
