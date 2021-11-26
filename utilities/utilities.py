import nextcord as discord
from nextcord.ext import commands
import re
import json


def clean_code(content) -> str:
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    return content


def read_json(file) -> dict:
    with open(f"{file}", "r") as f:
        data = json.load(f)
    return data


def write_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(f"{value} is an invalid time key")
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number")
        return time


class walbankconverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        if argument.lower() == "wallet":
            arg = argument.lower()
        elif argument.lower() == "bank":
            arg = argument.lower()
        else:
            raise commands.BadArgument(
                "Didn't specify whether it was wallet or bank properly"
            )

        return arg


class statusconverter(commands.Converter):
    async def convert(self, ctx, argument: str):
        if argument.lower() == "idle":
            return discord.Status.idle
        elif argument.lower() == "dnd" or argument.lower() == "do not disturb":
            return discord.Status.dnd
        elif argument.lower() == "invisible":
            return discord.Status.invisible
        elif argument.lower() == "online":
            return discord.Status.online
        else:
            raise commands.BadArgument("Didn't specify the status properly")
