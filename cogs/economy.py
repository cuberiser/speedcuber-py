import random
import nextcord as discord
from nextcord.ext import commands
from utilities.utilities import read_json, write_json, walbankconverter


class economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shopitems = {
            "qiyi ms": 7000,
            "gan 11 m pro": 50000,
            "rs3m 2020": 7000,
            "meilong m": 5000,
            "yuxin little magic m": 5500,
            "dayan guhong v4m": 14000,
            "yj mgc 5x5": 15000,
            "yj mgc 4x4": 17000,
            "yj mgc 2x2": 9000,
            "mgc elite 2x2": 17000
        }


    @commands.Cog.listener()
    async def on_ready(self):
        print("-" * 50)
        print(f"{self.qualified_name} loaded")

    @commands.command()
    async def urmom(self, ctx):
        await ctx.send("<@735411402386440272>")

    async def get_bal(self, user: discord.Member) -> dict:
        data = await self.bot.config.get(user.id)
        if not data or ("wallet" not in data) or ("bank" not in data) or ("inv" not in data):
            data = {"_id": user.id, "bank": 0, "wallet": 0, "inv": []}
            self.bot.config.upsert({"_id": user.id, "bank": 0, "wallet": 0, "inv": []})
        return data


    @commands.command(name="work", description="Work command")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def work(self, ctx):
        amt = random.randint(1000, 2000)
        bal = await self.get_bal(ctx.author)
        bal["wallet"] += amt
        write_json("economy.json", bal)
        embed = discord.Embed(
            title=f"{ctx.author} worked!",
            description=f"You worked and earned 💠{amt} coins",
        )
        await ctx.send(embed=embed)


    @commands.command(aliases=["deposit"])
    async def dep(self, ctx, *, amt):
        bal = await self.get_bal(ctx.author)
        try:
            amt = int(amt)
        except ValueError:
            if amt.lower() == "all" or amt.lower() == "max":
                amt = (await self.get_bal(ctx.author))
                amt = amt['wallet']
            else:
                raise commands.BadArgument("The amount is not proper")
        
        if amt > bal['wallet']:
            await ctx.send("Can't deposit more than you have!")
            return
        
        if amt <= 0:
            await ctx.send("Can't deposit negatives or 0")
            return
        
        bal["wallet"] -= amt
        bal["bank"] += amt
        write_json("economy.json", bal)
        await ctx.send(
            f"Sucessfully deposited **{amt}** coins to bank. Bank amount: {bal['bank']}"
        )


    @commands.command(name="with", aliases=["undeposit", 'withdraw'])
    async def with_(self, ctx, *, amt):
        bal = await self.get_bal(ctx.author)
        try:
            amt = int(amt)
        except ValueError:
            if amt.lower() == "all" or amt.lower() == "max":
                amt = (await self.get_bal(ctx.author))
                amt = amt['bank']
            else:
                raise commands.BadArgument("The amount is not proper")
        
        if amt > bal['bank']:
            await ctx.send("Can't withdraw more than you have!")
            return
        
        if amt <= 0:
            await ctx.send("Can't withdraw negatives or 0")
            return
        
        bal["wallet"] += amt
        bal["bank"] -= amt
        write_json("economy.json", bal)
        await ctx.send(
            f"Sucessfully withdrew **{amt}** coins to bank. Wallet amount: {bal['wallet']}"
        )


    @commands.command(aliases=["balance"])
    async def bal(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        balance = (await self.get_bal(user))

        emb = discord.Embed(title=f"{user}'s balance")
        emb.description = f'Wallet - 💠{balance["wallet"]}\nBank - 💠{balance["bank"]}\nNet worth - {balance["wallet"] + balance["bank"]}'
        emb.set_footer(icon_url=ctx.author.display_avatar.url, text=f'Requested by {ctx.author}')
        await ctx.send(embed=emb)
    
    def get_item_sellvalue(self, item):
        return self.shopitems[item] - ((self.shopitems[item])//10)

    @commands.command()
    async def shop(self, ctx, *, item=None):
        bal = (await self.get_bal(ctx.author))
        bal = bal['bank'] + bal['wallet']
        if item is None:
            embed = discord.Embed(title=f'{self.bot.user}\'s shop')
            txt = ""
            for item in self.shopitems:
                txt += f"\n{item} - \n\tprice: {(self.shopitems)[item]}\n\tsell value - {self.get_item_sellvalue(item)}\n\tbuyable? - {'❌' if bal < (self.shopitems)[item] else '✅'}\n"
            embed.description = txt
            embed.set_footer(text="Buyable signifies if your net worth is enough to buy the item")
            await ctx.send(embed = embed)
        else:
            try:
                item = (self.shopitems)[item.lower()]
            except commands.CommandInvokeError:
                await ctx.send(f"Invalid item - {item}, please check the spelling correctly")
                return
            await ctx.send(f"```\n{item} - \n\tprice: {(self.shopitems)[item]}\n\tsell value - {self.get_item_sellvalue(item)}\n\tbuyable? - {'❌' if bal < (self.shopitems)[item] else '✅'}\n```")

    @commands.command()
    async def buy(self, ctx, *, item):
        if item.lower() not in self.shopitems:
            await ctx.send("This is an invalid item")
            return
        item = item.lower()
        bal = await self.get_bal(ctx.author)
        if bal['wallet'] < self.shopitems[item]:
            if (bal['wallet'] + bal['bank']) >= self.shopitems[item]:
                await ctx.send(f"Your wallet balance isn't enough to buy this item but net worth is, so withdraw your coins to buy the item.")
            else:
                await ctx.send("Your balance is too low for this item")
            return
        if item not in bal['inv']:
            bal['inv'][item] = 1
        else:
            bal['inv'][item] += 1
        bal['wallet'] -= self.shopitems[item]
        write_json('economy.json', bal)
        await ctx.send(f"Sucessfully bought {item}")


    @commands.command()
    async def sell(self, ctx, *, item):
        if item.lower() not in self.shopitems:
            await ctx.send("This is an invalid item")
            return
        item = item.lower()
        bal = await self.get_bal(ctx.author)
        if item not in bal['inv']:
            await ctx.send("You don't own this item")
            return
        else:
            bal['inv'][item] -= 1
        bal['wallet'] += self.get_item_sellvalue(item)
        write_json('economy.json', bal)
        await ctx.send(f"Sucessfully sold {item}")
    

    @commands.command()
    async def inv(self, ctx, *, user: discord.Member=None):
        if user is None:
            user = ctx.author
        inv = (await self.get_bal(user))['inv']
        if len(inv) > 0:
            invtxt = "\n".join([f"{obj} - {inv[obj]}" for obj in inv])
        else:
            invtxt = "Nothing in your inventory"
        await ctx.send(invtxt)
    

    @commands.command(aliases=['am'])
    @commands.is_owner()
    async def addmoney(self, ctx, user: discord.User, wallet_bank: walbankconverter, amt: int):
        bal = await self.get_bal(user)
        bal[wallet_bank] += amt
        write_json('economy.json', bal)
        await ctx.send(f"Added {amt} to {user.mention}")
    

    @commands.command(aliases=['rm'])
    @commands.is_owner()
    async def removemoney(self, ctx, user: discord.User, wallet_bank: walbankconverter, amt: int):
        bal = await self.get_bal(user)
        bal[wallet_bank] -= amt
        write_json('economy.json', bal)
        await ctx.send(f"Removed {amt} from {user.mention}")


def setup(bot):
    bot.add_cog(economy(bot))
