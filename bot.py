from __future__ import annotations
# --- imports --- #

import discord, traceback, random, json, traceback, os, re, asyncio, datetime, math, io, time, sys, apftool, base1114112, hashlib, subprocess
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from typing import Literal
from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from PIL import Image

# --- setup --- #

os.makedirs("tags", exist_ok=True)
os.makedirs("snapins", exist_ok=True)

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

cfg = load_config()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='uni!', intents=intents)
tree = bot.tree
mariqueue = {}

snapins = []
snaps = False

# --- quick config --- #

evaluser = int(cfg["allowedModuleEditors"][0])
detectionTypes = ( "=", "==", "default", "DEFAULT", "author", "startswith", "STARTSWITH", "endswith", "ENDSWITH", "regex", "REGEX", "split", "SPLIT", "channel" )
memoryboxpages = {}

aliases = {} # aliases for tags
aliases["AUTHOR"] = "author"
aliases[""] = "default"
aliases["re"] = "regex"
aliases["RE"] = "REGEX"
aliases["CHANNEL"] = "channel"
aliases["starts"] = "startswith"
aliases["ends"] = "endswith"
aliases["STARTS"] = "STARTSWITH"
aliases["ENDS"] = "ENDSWITH"
aliases["contains"] = "default"
aliases["CONTAINS"] = "DEFAULT"
aliases["containscase"] = "DEFAULT"
aliases["CONTAINSCASE"] = "DEFAULT"
aliases["match"] = "="
aliases["matchcase"] = "=="
aliases["MATCH"] = "=="
aliases["MATCHCASE"] = "=="

minesweepere = {}
minesweepere["M"] = '||💥||'
minesweepere["0"] = '||▫️||'
minesweepere["1"] = '||1️⃣||'
minesweepere["2"] = '||2️⃣||'
minesweepere["3"] = '||3️⃣||'
minesweepere["4"] = '||4️⃣||'
minesweepere["5"] = '||5️⃣||'
minesweepere["6"] = '||6️⃣||'
minesweepere["7"] = '||7️⃣||'
minesweepere["8"] = '||8️⃣||'

e3cd_xyz = {}
e3cd_xyz["warn"] = 'warned'
e3cd_xyz["mute"] = 'muted'
e3cd_xyz["kick"] = 'kicked'
e3cd_xyz["ban"] = 'banned'
e3cd_xyz["removerole"] = 'stripped a role from'
e3cd_xyz["addrole"] = 'granted a role'

prefwords = ["hey unimeter ", "hey unimeter fucking ", "uni!", "unimeter!", "unimeter ", "unimeter, ", "hey unicycle "]

desc = {}
desc["Compact"] = """
bot made by mari2
Flowmeter made by tema5002.
### **Commands**
Say *hey unimeter add tag keyword;detection_type;reply;args* to **add new tag**
Say *hey unimeter remove tag keyword* to **remove tag**
Say *hey unimeter list tags* to **list existing tags on this server**
### **Tag Arguments**
- **keyword** - keyword which triggers the reply
- **detection_type**:
- - **default** (or blank) - triggers if **keyword** in message content
- - **split** - triggers only to whole words
- - **=** - match
- **reply** - a reply
- **args**
- - react - if this argument is specified then **reply** must be an emoji
- - delete - deletes the input message and output message
- - reply - replies to the message instead of sending in the channel
"""
desc["Normal"] = """
bot made by mari2
Flowmeter made by tema5002.
### **Commands**
Say *hey unimeter add tag keyword;detection_type;reply;args* to **add new tag**
Say *hey unimeter update tag keyword;detection_type;reply;args* to **update already existing tag**
Say *hey unimeter remove tag keyword* to **remove tag**
Say *hey unimeter list tags* to **list existing tags on this server**
### **Tag Arguments**
- **keyword** - keyword which triggers the reply
- **detection_type** (if uppercase its case sensetive except for =/==):
- - **default** (or blank) - triggers if **keyword** in message content (not case sensitive)
- - **split** - triggers only to whole words surrounded by spaces or end of string
- - **=** - match
- - **==** - exact match (case sensitive)
- - **startswith** - triggers when **message** starts with **keyword**
- - **endswith** - triggers when **message** ends with **keyword**
- - **regex** - regular expression
- **reply** - a reply
- **args**
- - react - if this argument is specified then **reply** must be an emoji
- - delete - deletes the input message and output message
- - remove - deletes only the input message
- - reply - replies to the message instead of sending in the channel
- - replyping - replies to the message instead of sending in the channel and pings the author
- - byuserUSER-ID - replies only if user id is this, you can chain these to respond to a few people
"""
desc["Large"] = """
bot made by mari2
Flowmeter made by tema5002.
### **Commands**
Say *hey unimeter add tag keyword;detection_type;reply;args* to **add new tag**
Say *hey unimeter update tag keyword;detection_type;reply;args* to **update already existing tag**
Say *hey unimeter remove tag keyword or tag* to **remove tag**
Say *hey unimeter remove tag_id tag_id* to **remove a tag by id**
Say *hey unimeter list tags* to **list existing tags on this server**
### **Tag Arguments**
- **keyword** - keyword which triggers the reply
- **detection_type** (if uppercase its case sensetive except for =/==, and for regex/REGEX which are backwards):
- - **default** (or blank) - triggers if **keyword** in message content (not case sensitive)
- - **split** - triggers only to whole words surrounded by spaces or end of string
- - **=** - match
- - **==** - exact match (case sensitive)
- - **startswith** - triggers when **message** starts with **keyword**
- - **endswith** - triggers when **message** ends with **keyword**
- - **regex** - regular expression
- - **author** - checks for **author id** instead of a **keyword**
- - **channel** - checks for **channel id** instead of a **keyword**
- **reply** - a reply
- **args**
- - react - if this argument is specified then **reply** must be an emoji
- - delete - deletes the input message and output message
- - remove - deletes only the input message
- - reply - replies to the message instead of sending in the channel
- - replyping - replies to the message instead of sending in the channel and pings the author
- - byuserUSER-ID - replies only if user id is this, you can chain these to respond to a few people
- - OR - process compound conditionals as OR instead of AND
### **Advanced**
- to pick replies at random for a message, do [*reply1*,*reply2*,*reply3*] in **square brackets**
- to get other words used in the message, you can do {args}. you can also do {args0...9} to get specific words
- to get a random number, use {random} (uses the same calcs as /metronome's mute)
- to get a the user, use {author}, to get the channel, use {channel}
- to have a var for the tag or users of the tag, use {var} and {var\_user} respectively. to increment or decrement them, use inc\_var/dec\_var as an arg.
- to use a var from other tags use {var\_*keyword*} and {var\_*keyword*\_user}/{var\_*keyword*USERID} respectively. to increment or decrement these, use inc\_var\_*keyword*/dec\_var\_*keyword* as an arg.
- **compounding conditionals**
- - Specified as &(keyword/detection_type) or !(keyword/detection_type)
- - & requires the conditional to be true, ! requires it to be false
"""

# --- commands --- #

class Kreisicoins(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    kreisicoins = app_commands.Group(
        name="kreisicoins",
        description="kreisicoin commands"
    )

    @kreisicoins.command(name="inventory", description="see your kreisicoins")
    async def inv(self, ctx: discord.Interaction, user: discord.User = None):
        try:
            await ctx.response.defer(ephemeral=False)
            if not user:
                user = ctx.user
            db = load_db(ctx.guild.id)
            db.setdefault("invs", {})
            db["invs"].setdefault(str(user.id), {})
            db["invs"][str(user.id)].setdefault("kreisicoins", 0)
            youHave = "you have"
            if user != ctx.user:
                youHave = f"{user.name} has"
            await ctx.followup.send(f"{youHave} {db['invs'][str(user.id)]['kreisicoins']} kreisicoins <:thubm_up:1096323451985334363><:biglipman:1146680272453124116><:normal:1173301276851843122><:slungus:1462591327446372373><:typing:1133071627370897580><:staring_cat:1097740776340992080>")
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @kreisicoins.command(name="add", description="magically give kreisicoins to user")
    @discord.app_commands.default_permissions(administrator=True)
    async def add(self, ctx: discord.Interaction, user: discord.User, reason: str = "NO FUCKING REASON", count: int = 1):
        try:
            if not ctx.user.id in [798072830595301406, 986132157967761408] and not ctx.user.guild_permissions.administrator:
                return await ctx.response.send_message("ok BRAINFUMBLER *converts all your code into brainfuck*")
            await ctx.response.defer(ephemeral=False)
            db = load_db(ctx.guild.id)
            db.setdefault("invs", {})
            db["invs"].setdefault(str(user.id), {})
            db["invs"][str(user.id)].setdefault("kreisicoins", 0)
            db["invs"][str(user.id)]["kreisicoins"] += count
            save_db(ctx.guild.id, db)
            await ctx.followup.send(f"*{user.name} has earned {count} kreisicoins for {reason}*\n-# *they now have {db['invs'][str(user.id)]['kreisicoins']} total kreisicoins*")
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @kreisicoins.command(name="remove", description="mysteriously delete kreisicoins from user")
    @discord.app_commands.default_permissions(administrator=True)
    async def remove(self, ctx: discord.Interaction, user: discord.User, reason: str = "NO FUCKING REASON", count: int = 1):
        try:
            if not ctx.user.id in [798072830595301406, 986132157967761408] and not ctx.user.guild_permissions.administrator:
                return await ctx.response.send_message("ok BRAINFUMBLER *converts all your code into brainfuck*")
            await ctx.response.defer(ephemeral=False)
            db = load_db(ctx.guild.id)
            db.setdefault("invs", {})
            db["invs"].setdefault(str(user.id), {})
            db["invs"][str(user.id)].setdefault("kreisicoins", 0)
            db["invs"][str(user.id)]["kreisicoins"] -= count
            save_db(ctx.guild.id, db)
            await ctx.followup.send(f"*{user.name} has lost {count} kreisicoins for {reason}*\n-# *they now have {db['invs'][str(user.id)]['kreisicoins']} total kreisicoins*")
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @kreisicoins.command(name="transfer", description="move kreisicoins to another user")
    async def transfer(self, ctx: discord.Interaction, user: discord.User, reason: str = "NO FUCKING REASON", count: int = 1):
        try:
            await ctx.response.defer(ephemeral=False)
            db = load_db(ctx.guild.id)
            db.setdefault("invs", {})
            db["invs"].setdefault(str(user.id), {})
            db["invs"].setdefault(str(ctx.user.id), {})
            db["invs"][str(user.id)].setdefault("kreisicoins", 0)
            db["invs"][str(ctx.user.id)].setdefault("kreisicoins", 0)
            if count < 0:
                return await ctx.followup.send("theft is illegal, dumbass")
            if count > db["invs"][str(ctx.user.id)]["kreisicoins"]:
                return await ctx.followup.send("insufficient funds for transfer")
            db["invs"][str(ctx.user.id)]["kreisicoins"] -= count
            db["invs"][str(user.id)]["kreisicoins"] += count
            save_db(ctx.guild.id, db)
            await ctx.followup.send(f"*you transferred {count} kreisicoins to {user.name} for {reason}*\n-# *they now have {db['invs'][str(user.id)]['kreisicoins']} total kreisicoins, you now have {db['invs'][str(ctx.user.id)]['kreisicoins']}*")
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @kreisicoins.command(name="bank", description="withdraw or deposit from bank")
    @app_commands.describe(count="positive for savings, negative for loan")
    async def transfer(self, ctx: discord.Interaction, count: int = 0):
        try:
            await ctx.response.defer(ephemeral=False)
            db = load_db(ctx.guild.id)
            db.setdefault("invs", {})
            db["invs"].setdefault(str(ctx.user.id), {})
            db["invs"][str(ctx.user.id)].setdefault("kreisicoins", 0)
            db["invs"][str(ctx.user.id)].setdefault("bank", 0)
            if count == 0:
                debt = "in savings"
                if 0 > db["invs"][str(ctx.user.id)]["bank"]:
                    debt = "in debt"
                await ctx.followup.send(f"you have {db['invs'][str(ctx.user.id)]['kreisicoins']} kreisicoins\nbank balance: {abs(db['invs'][str(ctx.user.id)]['bank'])} {debt}")
            else:
                if count > db["invs"][str(ctx.user.id)]["kreisicoins"]:
                    return await ctx.followup.send("you cannot deposit more than you own")
                db["invs"][str(ctx.user.id)]["kreisicoins"] -= count
                db["invs"][str(ctx.user.id)]["bank"] += count
                debt = "in savings"
                tofrom = f"deposited {abs(count)} kreisicoins"
                if 0 > count:
                    tofrom = f"withdrawn {abs(count)} kreisicoins"
                if 0 > db["invs"][str(ctx.user.id)]["bank"]:
                    debt = "in debt"
                    if -2000 > db["invs"][str(ctx.user.id)]["bank"]:
                        return await ctx.followup.send("loan rejected")
                save_db(ctx.guild.id, db)
                await ctx.followup.send(f"*you {tofrom} to the bank*\n-# *you now have {db['invs'][str(ctx.user.id)]['kreisicoins']} kreisicoins*\n-# *bank balance: {abs(db['invs'][str(ctx.user.id)]['bank'])} {debt}*")
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @kreisicoins.command(name="gamble", description="LETS GO GAMBLINGGGGGGGGGGGG!!!!!!!!!")
    async def gamble(self, ctx: discord.Interaction, count: int = 1, risk: Literal[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20] = 2):
        try:
            await ctx.response.defer(ephemeral=False)
            db = load_db(ctx.guild.id)
            db.setdefault("invs", {})
            db["invs"].setdefault(str(ctx.user.id), {})
            db["invs"][str(ctx.user.id)].setdefault("kreisicoins", 0)
            if count < 0:
                return await ctx.followup.send("theft is illegal, dumbass")
            if count > db["invs"][str(ctx.user.id)]["kreisicoins"]:
                return await ctx.followup.send("insufficient funds for gamble")
            db["invs"][str(ctx.user.id)]["kreisicoins"] -= count
            save_db(ctx.guild.id, db)
            await ctx.followup.send(f"*you gambled **{count}** kreisicoins!*")
            await asyncio.sleep(random.randint(3,7))
            db = load_db(ctx.guild.id)
            lost = "lost!"
            if random.randint(1,risk) == 1:
                lost = f"won!!! you gained **{count*(risk-1)}** kreisicoins and"
                db["invs"][str(ctx.user.id)]["kreisicoins"] += count*risk
            save_db(ctx.guild.id, db)
            await ctx.followup.send(f"*you {lost} you now have **{db['invs'][str(ctx.user.id)]['kreisicoins']}** total kreisicoins*")
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @kreisicoins.command(name="leaderboard", description="who has the kreisiest coins")
    async def leaderboard(self, ctx: commands.Interaction):
        try:
            await ctx.response.defer()
            db = load_db(str(ctx.guild.id))
            db.setdefault("invs", {})
            amount = 10
            if "invs" not in db or not db["invs"]:
                await ctx.response.send_message(f"no leaderboard <:thubm_what:1150405177464070144>", ephemeral=True)
                return

            kreisidict = {}
            for inv in db["invs"]:
                db["invs"][inv].setdefault("kreisicoins", 0)
                kreisidict[inv] = db["invs"][inv]["kreisicoins"]

            sortedlb = dict(sorted(kreisidict.items(), key=lambda item: item[1], reverse=True))

            leaderboard = ""
            counter = 0
            for member in sortedlb:
                counter += 1
                if counter > 10:
                    break
                leaderboard = leaderboard + f'{counter}. <@{member}>: {kreisidict[member]} kreisicoins\n'

            embed = discord.Embed(
                title=f'Top 10 kreisicoins:',
                color=discord.Color.blue(),
                description=leaderboard
            )

            await ctx.followup.send(embed=embed)
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

class TagCmd(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    tag = app_commands.Group(
        name="tag",
        description="tag commands"
    )

    @tag.command(name="add", description="add a tag")
    @app_commands.describe(keyword="keyword which triggers the reply", detectiontype="method for detecting keywords, default is containing, = is exact, == is exact case", payload="output the bot sends", args="arguments for the output, example 'react' reacts with an emojis instead of a message. to chain multiple, use ; like in the text commands")
    async def add(self, ctx: discord.Interaction, keyword: str, detectiontype: Literal[*detectionTypes], payload: str, args: str = ""):
        try:
            db = load_db(ctx.guild.id)
            db.setdefault("tags", [])
            if not str(ctx.user.id) in cfg["allowedModuleEditors"] and not ctx.user.guild_permissions.manage_guild:
                return await ctx.followup.send(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")
            await ctx.response.defer(ephemeral=False)

            tage = f"{keyword};{detectiontype};{payload}"
            if args:
                tage += f";{args}"

            if len(re.findall(r'(?<!\\);', tage)) < 2:
                return await ctx.followup.send(f"not enough semicolons\nformat: `keyword;detectionType;reply;args`")
            fragments = re.split(r'(?<!\\);', tage)
            fragments = [f.replace(r'\;', ';') for f in fragments]
            if not fragments[1] in detectionTypes and not fragments[1] in aliases:
                return await ctx.followup.send(f"invalid detection type <:picardia_dead:1122791287360323625>")
            if tage in db["tags"]:
                return await ctx.followup.send(f"this tag is already exist <:thubm_what:1150405177464070144>")
            await ctx.followup.send(f"added tag `{tage}` to **{ctx.guild}**")
            db["tags"].append(tage)
            save_db(ctx.guild.id, db)
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @tag.command(name="remove", description="remove a tag")
    @app_commands.describe(keyword="keyword which triggers the reply", detectiontype="method for detecting keywords, default is containing, = is exact, == is exact case", payload="output the bot sends", args="arguments for the output, example 'react' reacts with an emojis instead of a message. to chain multiple, use ; like in the text commands")
    async def rem(self, ctx: discord.Interaction, keyword: str, detectiontype: Literal[*detectionTypes] = None, payload: str = None, args: str = None):
        try:
            db = load_db(ctx.guild.id)
            db.setdefault("tags", [])
            await ctx.response.defer(ephemeral=False)
            if not str(ctx.user.id) in cfg["allowedModuleEditors"] and not ctx.user.guild_permissions.manage_guild:
                return await ctx.followup.send(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")

            dokeywordsearch = False
            tage = f"{keyword}"
            if detectiontype:
                tage += f";{detectiontype}"
                if payload:
                    tage += f";{payload}"
                    if args:
                        tage += f";{args}"
    
            fragments = re.split(r'(?<!\\);', tage)
            fragments = [f.replace(r'\;', ';') for f in fragments]
    
            if len(fragments) == 1:
                dokeywordsearch = True
    
            if dokeywordsearch:
                tagses = []
                for tag in db["tags"]:
                    frogments = re.split(r'(?<!\\);', tag)
                    frogments = [f.replace(r'\;', ';') for f in frogments]
                    if fragments[0] == frogments[0]:
                        tagses.append(tag)
                if len(tagses) == 1:
                    tage = tagses[0]
                elif len(tagses) == 0:
                    return await ctx.followup.send(f"this tag is already lacks existance <:thubm_what:1150405177464070144>")
                else:
                    ambi = "ambiguous tag label, please specify which tag you want to delete specifically (whole tag or use remove tag_id):\n```\n"
                    for index, tag in enumerate(db["tags"]):
                        if tag in tagses:
                            ambi += f"{index}. {tag}\n"
                    ambi += "```"
                    return await ctx.followup.send(ambi[:2000])
    
            if not tage in db["tags"]:
                return await ctx.followup.send(f"this tag is already lacks existance <:thubm_what:1150405177464070144>")
    
            await ctx.followup.send(f"removed tag `{tage}` from **{ctx.guild}**")
            db["tags"].remove(tage)
            save_db(ctx.guild.id, db)
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @tag.command(name="list", description="list all tags")
    async def rem(self, ctx: discord.Interaction, page: int = 1):
        try:
            db = load_db(ctx.guild.id)
            db.setdefault("tags", [])
            page = (int(page))*10
            merge = (str(ctx.guild.id) in cfg["slinxianServers"])
            embed = generatetaglist(str(ctx.guild.id), page, merge)
            view = MenuView(str(ctx.guild.id), page)
            view.message = await ctx.response.send_message(embed=embed, view=view)
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @tag.command(name="remove-by-id", description="remove tag using ID")
    async def rem(self, ctx: discord.Interaction, tagid: int):
        try:
            db = load_db(ctx.guild.id)
            await ctx.response.defer(ephemeral=False)
            if not str(ctx.user.id) in cfg["allowedModuleEditors"] and not ctx.user.guild_permissions.manage_guild:
                return await ctx.followup.send(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")
    
            if tagid > len(db["tags"])-1:
                return await ctx.followup.send("id out of range")
            else:
                rmtag = db["tags"].pop(tagid)
                save_db(ctx.guild.id, db)
                return await ctx.followup.send(f"removed tag `{rmtag}` from **{ctx.guild}**")
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @tag.command(name="update", description="replace tag with a new one using the same keyword")
    @app_commands.describe(keyword="keyword which triggers the reply", detectiontype="method for detecting keywords, default is containing, = is exact, == is exact case", payload="output the bot sends", args="arguments for the output, example 'react' reacts with an emojis instead of a message. to chain multiple, use ; like in the text commands")
    async def add(self, ctx: discord.Interaction, keyword: str, detectiontype: Literal[*detectionTypes], payload: str, args: str = ""):
        try:
            db = load_db(ctx.guild.id)
            db.setdefault("tags", [])
            await ctx.response.defer(ephemeral=False)
            if not str(ctx.user.id) in cfg["allowedModuleEditors"] and not ctx.user.guild_permissions.manage_guild:
                return await ctx.followup.send(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")

            tage = f"{keyword};{detectiontype};{payload}"
            if args:
                tage += f";{args}"
            tage_new = tage
    
            fragments = re.split(r'(?<!\\);', tage)
            fragments = [f.replace(r'\;', ';') for f in fragments]
    
            tagses = []
            for tag in db["tags"]:
                frogments = re.split(r'(?<!\\);', tag)
                frogments = [f.replace(r'\;', ';') for f in frogments]
                if fragments[0] == frogments[0]:
                    tagses.append(tag)
            if len(tagses) == 1:
                tage = tagses[0]
            elif len(tagses) == 0:
                return await ctx.followup.send(f"this tag is already lacks existance <:thubm_what:1150405177464070144>")
            else:
                ambi = "ambiguous tag label, please remove the tag you want to update specifically and create anew:\n```\n"
                for tag in tagses:
                    ambi += f"{tag}\n"
                ambi += "```"
                return await ctx.followup.send(ambi[:2000])
    
            await ctx.followup.send(f"updated tag `{tage}` to `{tage_new}` in **{ctx.guild}**")
            db["tags"][(db["tags"].index(tage))] = tage_new
            save_db(ctx.guild.id, db)
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

    @tag.command(name="export", description="exports tags into txt file")
    async def export(self, ctx: discord.Interaction):
        try:
            db = load_db(ctx.guild.id)
            db.setdefault("tags", [])
            await ctx.response.defer(ephemeral=False)
            if not str(ctx.user.id) in cfg["allowedModuleEditors"] and not ctx.user.guild_permissions.manage_guild:
                return await ctx.followup.send(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")

            tagthing = db["tags"]
            tagthing_escapedlinefeeds = []
            for tag in tagthing:
                tagthing_escapedlinefeeds.append(tag.replace("\n", "\\n"))

            tagthingstr = "\n".join(tagthing_escapedlinefeeds)

            exportedtags = discord.File(
                io.BytesIO(tagthingstr.encode("utf-8")),
                filename=f"flowmeter_rsc_export_{ctx.guild.name}.txt"
            )
    
            await ctx.followup.send(f"exported tags for **{ctx.guild}**", file=exportedtags)
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="fire", description="burns the chat")
async def fire(ctx: commands.Context):
    try:
        await ctx.response.defer(ephemeral=True)
        if not str(ctx.user.id) in cfg["allowedModuleEditors"] and not ctx.user.guild_permissions.manage_guild:
            return await ctx.followup.send(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")
        messages = [msg async for msg in ctx.channel.history(limit=10)]
        db = load_db(ctx.guild.id)
        channel = None
        if "logchannel" in db:
            channel = bot.get_channel(db["logchannel"])
        if channel:
            await channel.send(f"<@{ctx.user.id}> set <#{ctx.channel.id}> on fire for some fucking reason!", allowed_mentions=discord.AllowedMentions.none())
        for msg in messages:
            await msg.add_reaction("🔥")
        await ctx.followup.send(":x: task failed to fail")
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="minesweeper", description="Play Minesweeper")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def minesweeper(ctx: commands.Context):
    try:
        await ctx.response.defer()
        boardsize = 9
        mines = 10

        boardtemp = []
        for num in range(boardsize):
            boardtemp.append("0")

        board = []
        for num in range(boardsize):
            board.append(boardtemp[:])

        for mine in range(mines):
            x = random.randint(0, boardsize-1)
            y = random.randint(0, boardsize-1)
            while board[y][x] == "M" or (x < 2 and y < 2):
                x = random.randint(0, boardsize-1)
                y = random.randint(0, boardsize-1)
            board[y][x] = "M"

        for cy in range(boardsize):
            for cx in range(boardsize):
                if board[cy][cx] == "M":
                    continue

                mines = 0

                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue

                        ny = cy + dy
                        nx = cx + dx

                        if 0 <= nx < boardsize and 0 <= ny < boardsize:
                            if board[ny][nx] == "M":
                                mines += 1

                board[cy][cx] = str(mines)
        
        final = ""
        for arrey in board:
            for char in arrey:
                final += char
            final += "\n"

        for char in minesweepere:
            final = final.replace(char, minesweepere[char])

        sentcmd = await ctx.followup.send(final[:2000])
        await sentcmd.add_reaction("🚩")
        await sentcmd.add_reaction("💥")
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="download-ram", description="download ram for pc today no scam ✅✅🔥☑️💯💯✅🔥✅✅✅🔥☑️☑️🔥💯")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ram(ctx: commands.Context):
    try:
        await ctx.response.defer(ephemeral=False)
        if random.randint(0, 1):
            await ctx.followup.send(f'sorry but because of QT-AI I have no ram to give you')
        else:    
            randomnum = random.random()
            kreisi = randomnum * 8192
            sane = int(kreisi)

            await ctx.followup.send(f'unimeter has sucessfully downloaded {sane}MB of ram to somewhere <:slungus:1462591327446372373>')
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="metronome", description="does a random mod action to a user")
@app_commands.describe(user="Select a user", reason="Enter a reason", override="removes possible outcomes from the command")
@discord.app_commands.default_permissions(ban_members=True)
async def metronome(ctx: commands.Context, user: discord.User, reason: str = "NO FUCKING REASON", override: Literal["safe", "mute", "idi nahui", "role"] = None):
    try:
        await ctx.response.defer(ephemeral=False)
        if override == "safe":
            actions = ["warn", "warn", "warn", "mute", "mute", "warn", "removerole", "addrole", "removerole", "addrole"]
        elif override == "mute":
            actions = ["mute"]
        elif override == "idi nahui":
            actions = ["kick", "ban"]
        elif override == "role":
            actions = ["addrole", "removerole"]
        else:
            actions = ["warn", "warn", "warn", "mute", "mute", "warn", "kick", "ban", "removerole", "addrole", "removerole", "addrole"]
        db = load_db(ctx.guild.id)
        channel = None
        if "logchannel" in db:
            channel = bot.get_channel(db["logchannel"])

        action = random.choice(actions)
        actiontext = e3cd_xyz[action]
        addline = ""

        try:
            if action == "mute":
                total = orderrandom()
                addline = f" for {total} seconds"
                await user.timeout(timedelta(seconds=total), reason=reason)
            elif action == "kick":
                await ctx.guild.kick(user, reason=reason)
            elif action == "ban":
                await ctx.guild.ban(user, reason=reason, delete_message_seconds=0)
            elif action == "removerole":
                taketh_away = random.choice(user.roles)
                await user.remove_roles(taketh_away, reason=reason)
                addline = f" (`{taketh_away.name}`)"
            elif action == "addrole":
                roles = [role for role in ctx.guild.roles if not role.managed]
                giveth = random.choice(roles)
                attemps = 0
                while giveth in user.roles and attemps <= 100:
                    giveth = random.choice(roles)
                    attemps += 1
                if attemps > 100:
                    raise Exception("100 attemps exceeded")
                await user.add_roles(giveth, reason=reason)
                addline = f" (`{giveth.name}`)"

        except Exception as e:
            print(e)
            await ctx.followup.send("<:cantaloupe:1322613311308693556> cant")
            return

        res = f"<@{ctx.user.id}> used metronome!\n<@{user.id}> was {actiontext}{addline} by <@{ctx.user.id}> for `{reason}`!"
        try:
            await user.send(f"sorry nerd but you've been hit with metronome which might've {actiontext} you from {ctx.guild} because of `{reason}`")
        except Exception:
            res += " (couldn't dm)"
        if channel:
            await channel.send(res, allowed_mentions=discord.AllowedMentions.none())
        await ctx.followup.send(res)
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="logchannel", description="sets a channel for logging")
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(channel = 'channel to use for logging')
async def logchannel(ctx: commands.Context, channel: discord.TextChannel):
    try:
        await ctx.response.defer(ephemeral=False)

        db = load_db(ctx.guild.id)
        db["logchannel"] = channel.id
        save_db(ctx.guild.id, db)

        await ctx.followup.send(f"set <#{channel.id}> as the logging channel for this server")
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="unkreisichannel", description="sets a channel for not spawning kreisicoins")
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(channel = 'channel to use for logging')
async def logchannel(ctx: commands.Context, channel: discord.TextChannel, remove: bool = False):
    try:
        await ctx.response.defer(ephemeral=False)

        db = load_db(ctx.guild.id)
        db.setdefault("unkreisi", [])
        un = ""
        if remove:
            un = "un"
            if str(channel.id) in db["unkreisi"]:
                db["unkreisi"].remove(str(channel.id))
        else:
            if not str(channel.id) in db["unkreisi"]:
                db["unkreisi"].append(str(channel.id))

        save_db(ctx.guild.id, db)

        await ctx.followup.send(f"{un}set <#{channel.id}> as an unkreisi channel for this server")
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="kreisichannel", description="sets a channel for spawning kreisicoins (excludes all other channels)")
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(channel = 'channel to set for kreisicoins')
async def logchannel(ctx: commands.Context, channel: discord.TextChannel, remove: bool = False):
    try:
        await ctx.response.defer(ephemeral=False)

        db = load_db(ctx.guild.id)
        db.setdefault("kreisi", [])
        un = ""
        if remove:
            un = "un"
            if str(channel.id) in db["kreisi"]:
                db["kreisi"].remove(str(channel.id))
        else:
            if not str(channel.id) in db["kreisi"]:
                db["kreisi"].append(str(channel.id))

        save_db(ctx.guild.id, db)

        await ctx.followup.send(f"{un}set <#{channel.id}> as an kreisi channel for this server")
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="ok-bro", description="Replies with ok bro!")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def okbro(ctx: commands.Context):
    try:
        await ctx.response.defer(ephemeral=False)

        await ctx.followup.send("ok bro")
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="obliterate", description="obliterates unimeter for 30 seconds")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def okbro(ctx: commands.Context):
    try:
        db = load_db(ctx.guild.id)
        if not str(ctx.user.id) in cfg["allowedModuleEditors"]:
            return await ctx.followup.send(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")

        await ctx.response.send_message("WHAT THE FU- *explodes*")
        time.sleep(30) # blocking function because fuck unimeter
        await ctx.followup.send(f"{ctx.user.name.upper()}\nWHAT THE FUCK\nWHY WOULD YOU DO THAT\nI THOUGHT WE WERE FRIENDS\nI THOUGHT YOU RESPECTED ME\nBUT APPARENTLY I WAS WRONG\nI'M SERIOUSLY CONSIDERING BLOCKING YOU RIGHT NOW\nTHIS IS NOT OKAY\nTHIS IS NOT FUNNY")
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="base1114112", description="encode/decode base1114112")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def baseoneoneoneidfk(ctx: commands.Context, data: str, encode: bool = False):
    try:
        await ctx.response.defer(ephemeral=False)
        if encode:
            await ctx.followup.send(base1114112.encode(int(data)))
        else:
            await ctx.followup.send(base1114112.decode(data))
    except Exception as e:
        try:
            await ctx.followup.send(f"500 internal server error\n-# {e}")
        except Exception as e:
            await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="ping", description="Replies with ping!")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ping(ctx: commands.Context):
    try:
        await ctx.response.defer(ephemeral=False)

        await ctx.followup.send(f"{round(bot.latency *1000)}ms")
    except Exception as e:
        await ctx.channel.send(f"{round(bot.latency *1000)}ms<:thubm_what:1150405177464070144>")

@tree.command(name="splash", description="replies with a splash message")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(id = 'uhhhhhh')
async def ping(ctx: commands.Context, id: int = None):
    try:
        if id is None:
            id = random.randint(0, len(cfg['startupMessages'])-1)
        if 1 > id:
            await ctx.response.send_message("ok brofork")
            return       
        if id > len(cfg["startupMessages"]):
            await ctx.response.send_message(f"limit is {len(cfg['startupMessages'])}")
            return
        await ctx.response.send_message(cfg["startupMessages"][id-1])
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="unimeter", description="Unimeter Digital Moisture meter for grain")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(input = 'The item to rate', type = 'The peramitor to rate')
async def unimeter(ctx: commands.Context, input: str, type: str = "wet"):
    try:
        await ctx.response.defer(ephemeral=False)

        seed = None
        if (type == "wet"):
            seed = hash_string(input)
        else:
            seed = hash_string(f'{input} (#*$&938r3tu3HTLIt8) {type}')

        rng = random.Random(seed)
        rand = rng.random();
        rating = round((rand * 100),1);
        diff = round((random.random() * 5),1)
        innac = round(((random.random() - 0.5) * diff),1);

        await ctx.followup.send(f'{input} is about {round((rating-innac),1)}% (±{round((diff/2),1)}%) {type}.');
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="say", description="Hello I am a Unimeter")
async def poland(ctx: commands.Context, msg: str, replyid: str = None, replyping: bool = False, attachment: discord.Attachment = None):
    try:
        if not ctx.user.id in [798072830595301406, 986132157967761408]:
            return await ctx.response.send_message("ok BRAINFUMBLER *converts all your code into brainfuck*", ephemeral=True)
        await ctx.response.defer(ephemeral=True)
        replyto = None
        file = None
        if attachment:
            data = await attachment.read()
            buffer = io.BytesIO(data)
            file = discord.File(fp=buffer, filename=f"UNIMETER_{attachment.filename}")
        if replyid:
            try:
                replyto = await ctx.channel.fetch_message(replyid)
            except Exception as e:
                return await ctx.followup.send(f"error {e}")
        if replyto:
            if replyping:
                await replyto.reply(msg, file=file)
            else:
                await replyto.reply(msg, file=file, allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.channel.send(msg, file=file)
            await ctx.followup.send(f"sent")
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="react", description="not quite fakenitro")
async def poland(ctx: commands.Context, emoji: str, msgid: str):
    try:
        if not ctx.user.id in [798072830595301406, 986132157967761408]:
            return await ctx.response.send_message("ok BRAINFUMBLER *converts all your code into brainfuck*", ephemeral=True)
        await ctx.response.defer(ephemeral=True)
        replyto = None
        try:
            replyto = await ctx.channel.fetch_message(msgid)
        except Exception as e:
            return await ctx.followup.send(f"error {e}")
        try:
            await replyto.add_reaction(emoji)
        except Exception as e:
            return await ctx.followup.send(f"error {e}")
        await ctx.followup.send(f"reacted")
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="check", description="check by which tags a message triggered")
@app_commands.describe(msg = 'who can it be now? 🎷🐛', user = 'spoof a user')
async def czech(ctx: commands.Context, msg: str, user: discord.User = None):
    try:
        await ctx.response.defer(ephemeral=False)
        if user is None:
            user = ctx.user

        merge = (str(ctx.guild.id) in cfg["slinxianServers"])
        db = load_db(ctx.guild.id, merge)
        db.setdefault("tags", [])
        tagslist = ""
        for tag in db["tags"]:
            fragments = re.split(r'(?<!\\);', tag)
            fragments = [f.replace(r'\;', ';') for f in fragments]
            message = DummyMessage(ctx, msg, user)
            print(fragments)
            trigger = resolvetag(message, fragments)
            if trigger:
                trigger = checkargs(message, fragments)
                if trigger:
                    tagslist += f"* {tag}\n"

        if not tagslist:
            return await ctx.followup.send("null <:fluent_bug:1462307350789623902>")

        embed = discord.Embed(
            title=f"This was triggered by {len(tagslist.splitlines())} tags",
            description=tagslist,
            color=discord.Color.from_rgb(0x46, 0x78, 0x52)
        )

        await ctx.followup.send(embed=embed)
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="get_ropl", description="bug with saxophone")
async def ropl(ctx: commands.Context):
    try:
        await ctx.response.defer(ephemeral=False)

        db = load_db("GLOBAL")
        db.setdefault("ropl", {})

        tagslist = ""
        for user in db["ropl"]:
            tagslist += f"<@{user}>: {db['ropl'][user]}\n"

        embed = discord.Embed(
            title=f"ROPL™️ (also known as react on ping list)",
            description=(f"{len(db['ropl'])} people are in react on ping list\n"+tagslist),
            color=discord.Color.from_rgb(0x46, 0x78, 0x52)
        )

        await ctx.followup.send(embed=embed)
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="set_ropl", description="bug with saxophone")
async def givemeropl(ctx: commands.Context, emoji: str = None):
    try:
        await ctx.response.defer(ephemeral=False)

        db = load_db("GLOBAL")
        db.setdefault("ropl", {})

        if emoji is None:
            del db["ropl"][str(ctx.user.id)]
            await ctx.followup.send(f"unset your react on ping")
        else:
            db["ropl"][str(ctx.user.id)] = emoji
            await ctx.followup.send(f"set your react on ping to {emoji}")
        save_db("GLOBAL", db)

    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="help", description="get help")
@app_commands.describe(ephemeral = 'make help dismissable', size = 'how extensive help should be')
async def help(ctx: commands.Context, ephemeral: bool = True, size: Literal["Compact", "Normal", "Large"] = "Normal"):
    try:
        await ctx.response.defer(ephemeral=ephemeral)
        embed = discord.Embed(
            title="Flowmeter-RSC Format",
            description=desc[size],
            color=discord.Color.from_rgb(0x46, 0x78, 0x52)
        )
        embed.set_footer(text=f"viewing page {size}")

        await ctx.followup.send(embed=embed);
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="memorybox", description="view a random image you sent in the past")
async def ping(ctx: commands.Context, user: discord.User = None):
    if user is None:
        user = ctx.user
    try:
        global memoryboxpages
        db = load_db(ctx.guild.id)
        await ctx.response.defer(ephemeral=False)
        memoryboxpages.setdefault(str(ctx.guild.id), {})
        memoryboxpages[str(ctx.guild.id)].setdefault(str(user.id), 0)
        pages = memoryboxpages[str(ctx.guild.id)][str(user.id)]
        offset = random.randint(0, pages)*25
        try:
            search = await bot.http.request(discord.http.Route("GET", f"/guilds/{ctx.guild.id}/messages/search?author_id={user.id}&has=image&sort_by=timestamp&sort_order=desc&offset={offset}"))
        except Exception:
            return await ctx.followup.send("SLOW THE FUCK DOWN")
        total_results = search.get('total_results', 0)

        if total_results == 0:
            await ctx.followup.send(f"no images <:thubm_what:1150405177464070144>")
            return

        repages = math.ceil(total_results/25)-1 # recalcs pages based on new search, if it has more pages, do another search and update pages
        if repages > 399:
            repages = 399
        if not (pages == repages):
            offset = random.randint(0, repages)*25
            try:
                search = await bot.http.request(discord.http.Route("GET", f"/guilds/{ctx.guild.id}/messages/search?author_id={user.id}&has=image&sort_by=timestamp&sort_order=desc&offset={offset}"))
                memoryboxpages[str(ctx.guild.id)][str(user.id)] = repages
            except Exception:
                return await ctx.followup.send("SLOW THE FUCK DOWN")

        if not search or not 'messages' in search or not search['messages']:
            await ctx.followup.send("<:thubm_what:1150405177464070144>")
            return
        search_sane = search['messages']
        message = random.choice(search_sane)[0]
        lookfor = None
        tries = 0
        while lookfor is None:
            if tries > 10:
                return await ctx.followup.send('Hey, catch me later, I\'ll buy you an image.')
            if message['attachments'] and message['embeds']:
                lookfor = random.choice(("attachments", "embeds"))
                break
            elif message['attachments']:
                lookfor = "attachments"
                break
            elif message['embeds']:
                lookfor = "embeds"
                break
            message = random.choice(search_sane)[0]

        thing = random.choice(message[lookfor])
        url = thing.get('url', 'Hey, catch me later, I\'ll buy you an image.')
        await ctx.followup.send(str(url))
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="nametest", description="Explore new names!!!!!!!!!!!")
@app_commands.describe(name= 'who can it be now? 🎷🐛')
async def czech(ctx: commands.Context, name: str):
    try:
        name_pos = name+"'s"
        if name.endswith('s'):
            name_pos = name+"'"
        name = "**"+name+"**"
        name_pos = "**"+name_pos+"**"

        sots = ["[[name]] is walking down the street on a nice sunny day.", "[[name]] just got crushed by a boulder.", "[[name]] just ate 17 raw eggs that is kreisi."]
        oots = ["The dog is chasing [[name]] down the street.", "The kreisler won't leave [[name]] alone.", "The CIA got [[name]]'s ass."]
        pd = ["The ball belongs to [[name]].", "Defeating the giant evil man is the responsibility of [[name]].", "The 'small' Black Hole belongs to [[name]]."]
        pp = ["The ball is [[name]].", "[[name]] cat just escaped.", "[[name]] mother :joy::joy::joy:"]
        btt = ["Hey [[name]], how are you doing today?", "Hello [[name]], we would like to call you about your car's extended warrenty", "yo [[name]], please delete your stupid fucking discord bot"]

        embed = discord.Embed(
            title="Name Tester",
            description="Explore new names!",
            color=discord.Color.from_rgb(0x46, 0x78, 0x52)
        )

        embed.add_field(name="Subject of the sentence", value=random.choice(sots).replace('[[name]]', name), inline=False)
        embed.add_field(name="Object of the sentence", value=random.choice(oots).replace('[[name]]', name), inline=False)
        embed.add_field(name="Possessive Determiner", value=random.choice(pd).replace('[[name]]', name), inline=False)
        embed.add_field(name="Possessive Pronoun", value=random.choice(pp).replace('[[name]]', name_pos), inline=False)
        embed.add_field(name="Being talked too", value=random.choice(btt).replace('[[name]]', name), inline=False)

        await ctx.response.send_message(embed=embed)
    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@tree.command(name="fuck", description="fuck!")
async def czech(ctx: commands.Context):
    try:
        if not ctx.user.id == evaluser:
            return await ctx.response.send_message("you do not have fucking permission")

        embed = discord.Embed(
            title="Fuck",
            description="Fuck",
            color=discord.Color.from_rgb(0x46, 0x78, 0x52)
        )

        embed.add_field(name="Fuck", value="Fuck", inline=False)
        
        await ctx.response.send_message(content="Fuck", embed=embed)

        process = subprocess.Popen("sudo -S killall lightdm", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate(input="1".encode())

    except Exception as e:
        await ctx.channel.send(f"500 internal server error\n-# {e}")

@app_commands.context_menu(name="convertapf")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def convertapf(interaction: discord.Interaction, message: discord.Message):
    try:
        await interaction.response.defer()
    except Exception as e:
        await interaction.channel.send(f"500 internal server error\n-# {e}")
        return

    if not message.attachments:
        await interaction.followup.send("no file")
        return

    attachment = message.attachments[0]
    data = await attachment.read()

    if data is None:
        await interaction.followup.send("failed to get data")
        return

    name, ext = os.path.splitext(attachment.filename)
    ext = ext.lower()

    try:
        # APF/AF2 -> PNG
        if ext in apftool.extensions_all:
            png_bytes = apftool.decodeany(data)

            if png_bytes.startswith(b"GIF"):
                ext = ".gif"
            else:
                ext = ".png"

            file = discord.File(
                io.BytesIO(png_bytes),
                filename=name + ext
            )

        # Image -> APF
        elif attachment.content_type and attachment.content_type.startswith("image/"):
            apfdata = apftool.encodeapf(data, 100, True)

            file = discord.File(
                io.BytesIO(apfdata.encode("utf-8")),
                filename=name + ".apf"
            )

        else:
            await interaction.followup.send("file must be an image, .apf, or .af2")
            return

        await interaction.followup.send(file=file)

    except Exception as e:
        await interaction.followup.send(f"conversion failed because of {e}")

bot.tree.add_command(convertapf)

@app_commands.context_menu(name="convertaf2")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def convertaf2(interaction: discord.Interaction, message: discord.Message):
    try:
        await interaction.response.defer()
    except Exception as e:
        await interaction.channel.send(f"500 internal server error\n-# {e}")
        return

    if not message.attachments:
        await interaction.followup.send("no file")
        return

    attachment = message.attachments[0]
    data = await attachment.read()

    if data is None:
        await interaction.followup.send("failed to get data")
        return

    name, ext = os.path.splitext(attachment.filename)
    ext = ext.lower()

    try:
        # APF/AF2 -> PNG
        if ext in apftool.extensions_all:
            png_bytes = apftool.decodeany(data)

            if png_bytes.startswith(b"GIF"):
                ext = ".gif"
            else:
                ext = ".png"

            file = discord.File(
                io.BytesIO(png_bytes),
                filename=name + ext
            )

        # Image -> APF
        elif attachment.content_type and attachment.content_type.startswith("image/"):
            apfdata = apftool.encodeaf2(data, 1, False, False, True)

            file = discord.File(
                io.BytesIO(apfdata.encode("utf-8")),
                filename=name + ".af2"
            )

        else:
            await interaction.followup.send("file must be an image, .apf, or .af2")
            return

        await interaction.followup.send(file=file)

    except Exception as e:
        await interaction.followup.send(f"conversion failed because of {e}")

bot.tree.add_command(convertaf2)

@app_commands.context_menu(name="convertwbmp")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def convertwbmp(interaction: discord.Interaction, message: discord.Message):
    try:
        await interaction.response.defer()
    except Exception as e:
        await interaction.channel.send(f"500 internal server error\n-# {e}")
        return

    if not message.attachments:
        await interaction.followup.send("no file")
        return

    attachment = message.attachments[0]
    data = await attachment.read()

    if data is None:
        await interaction.followup.send("failed to get data")
        return

    name, ext = os.path.splitext(attachment.filename)
    ext = ext.lower()

    try:
        # WBMP -> PNG
        if ext in apftool.extensions_all:
            png_bytes = apftool.decodeany(data)

            ext = ".png"

            file = discord.File(
                io.BytesIO(png_bytes),
                filename=name + ext
            )

        # Image -> WBMP
        elif attachment.content_type and attachment.content_type.startswith("image/"):
            img = Image.open(io.BytesIO(data))
            apfdata = apftool.encodewbmp(img)

            file = discord.File(
                io.BytesIO(apfdata),
                filename=name + ".wbmp"
            )

        else:
            await interaction.followup.send("file must be an image or .wbmp")
            return

        await interaction.followup.send(file=file)

    except Exception as e:
        await interaction.followup.send(f"conversion failed because of {e}")

bot.tree.add_command(convertwbmp)

@app_commands.context_menu(name="convertotb")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def convertotb(interaction: discord.Interaction, message: discord.Message):
    try:
        await interaction.response.defer()
    except Exception as e:
        await interaction.channel.send(f"500 internal server error\n-# {e}")
        return

    if not message.attachments:
        await interaction.followup.send("no file")
        return

    attachment = message.attachments[0]
    data = await attachment.read()

    if data is None:
        await interaction.followup.send("failed to get data")
        return

    name, ext = os.path.splitext(attachment.filename)
    ext = ext.lower()

    try:
        # OTB -> PNG
        if ext in apftool.extensions_all:
            png_bytes = apftool.decodeany(data)

            ext = ".png"

            file = discord.File(
                io.BytesIO(png_bytes),
                filename=name + ext
            )

        # Image -> OTB
        elif attachment.content_type and attachment.content_type.startswith("image/"):
            img = Image.open(io.BytesIO(data))
            apfdata = apftool.encodeotab(img)

            file = discord.File(
                io.BytesIO(apfdata),
                filename=name + ".otb"
            )

        else:
            await interaction.followup.send("file must be an image or .otb")
            return

        await interaction.followup.send(file=file)

    except Exception as e:
        await interaction.followup.send(f"conversion failed because of {e}")

bot.tree.add_command(convertotb)


@app_commands.context_menu(name="checksums")
@app_commands.user_install()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def checksums(interaction: discord.Interaction, message: discord.Message):
    try:
        await interaction.response.defer()
    except Exception as e:
        await interaction.channel.send(f"500 internal server error\n-# {e}")
        return

    if not message.attachments:
        await interaction.followup.send("no file")
        return

    attachment = message.attachments[0]
    data = await attachment.read()

    if data is None:
        await interaction.followup.send("failed to get data")
        return

    try:
        md5 = hashlib.md5(data).hexdigest()
        sha256 = hashlib.sha256(data).hexdigest()
        name, ext = os.path.splitext(attachment.filename)
        size = getfilesize(len(data))
        await interaction.followup.send(f"```\n{name}{ext}          {size}\nMD5: {md5}\nSHA256: {sha256}```")
    except Exception as e:
        await interaction.followup.send(f"conversion failed because of {e}")

bot.tree.add_command(checksums)

# --- misc functions --- #

class DummyMessage:
    def __init__(self, interaction: discord.Interaction, content: str, user: discord.User):
        self.content = content
        self.author = user
        self.channel = interaction.channel
        self.guild = interaction.guild
        self.id = None  # optional
        self.created_at = discord.utils.utcnow()

def getfilesize(size: int):
    ext = "B"
    if size > 2048:
        size = size / 1024
        ext = "KB" # binary Kilobytes
    if size > 2048:
        size = size / 1024
        ext = "MB" # binary megabytes
    if size > 2048:
        size = size / 1024
        ext = "GB" # binary gigabytes
    if size > 2048:
        size = size / 1024
        ext = "TB" # binary terabytes
    if size > 2048:
        size = size / 1024
        ext = "PB" # what
    return f"{round(size, 3)} {ext}"

def load_db(sid, merge=False):
    try:
        with open(f'tags/{sid}.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if merge:
        try:
            with open('tags/1042064947867287643.json', 'r') as f:
                merge_data = json.load(f)
        except FileNotFoundError:
            merge_data = {}

        # Merge only the 'tags' list
        if "tags" in merge_data:
            if "tags" not in data:
                data["tags"] = []
            # Concatenate lists
            data["tags"] += merge_data["tags"]

    return data

def save_db(sid, data):
    with open(f'tags/{sid}.json', 'w') as f:
        json.dump(data, f, indent=4)

def orderrandom(orders: int = 6):
    return int((10**random.randint(1, orders))*random.random())

def resolvetag(message, fragments: list, length: str = 2):
    if len(fragments) > length:
        if fragments[1] in aliases:
            fragments[1] = aliases[fragments[1]]

        if fragments[1] == "=":
            return message.content.lower() == fragments[0].lower()
        elif fragments[1] == "==":
            return message.content == fragments[0]
        elif fragments[1] == "default":
            return fragments[0].lower() in message.content.lower()
        elif fragments[1] == "DEFAULT":
            return fragments[0] in message.content
        elif fragments[1] == "author":
            return fragments[0] == str(message.author.id)
        elif fragments[1] == "channel":
            return  fragments[0] == str(message.channel.id)
        elif fragments[1] == "startswith":
            return message.content.lower().startswith(fragments[0].lower())
        elif fragments[1] == "STARTSWITH":
            return message.content.startswith(fragments[0])
        elif fragments[1] == "endswith":
            return message.content.lower().endswith(fragments[0].lower())
        elif fragments[1] == "ENDSWITH":
            return message.content.endswith(fragments[0])
        elif fragments[1] == "regex":
            return bool(re.search(fragments[0], message.content, re.IGNORECASE))
        elif fragments[1] == "REGEX":
            return bool(re.search(fragments[0], message.content))
        elif fragments[1] == "split":
            return fragments[0].lower() in message.content.lower().split()
        elif fragments[1] == "SPLIT":
            return fragments[0] in message.content.split()
        else:
            print(f"Warning: tag \"{fragments[0]};{fragments[1]}\" uses an unknown detection type!")
    else:
        print(f"Warning: tag \"{fragments[0]};{fragments[1]}\" is malformed!")

def checkargs(message, fragments):
    ormode = False
    orct = False
    if 'OR' in fragments[3:]:
        ormode = True

    for arg in fragments[3:]:
        if (arg.startswith("!(") or arg.startswith("&(")) and arg.endswith(")"):
            mode = True
            checked = False
            if arg[0] == "!":
                mode = False
            partition = re.split(r'(?<!\\)\/', arg[2:-1])
            if not len(partition) == 2:
                print("compound does not have a forward slash to split on")
                return False
            partition[0] = partition[0].replace(r'\/', '/')
            partition[1] = partition[1].replace(r'\/', '/')
            checked = resolvetag(message, partition, 1)
            if ormode:
                if checked == mode:
                    orct = True
            else:
                if not checked == mode:
                    return False
    if ormode:
        if not orct:
            return False
    if any("byuser" in fragment.lower() for fragment in fragments[3:]) and not f"byuser{message.author.id}" in fragments[3:]:
        return False
    return True

async def resolveoutcome(message, fragments):
    db = load_db(message.guild.id)
    db.setdefault("vars", {})
    db.setdefault("var_by_user", {})
    db["var_by_user"].setdefault(str(message.author.id), {})

    cont = checkargs(message, fragments)
    if not cont:
        return

    weeou = None
    response = fragments[2]
    if response.startswith("[") and response.endswith("]"):
        outcomes = re.split(r'(?<!\\),', response[1:-1])
        outcomes = [o.replace(r'\,', ',') for o in outcomes]
        response = random.choice(outcomes)

    vari = {}

    vari["author"] = message.author.name
    vari["channel"] = message.channel.name

    if "{args" in fragments[2]:
        start = message.content.lower().find(fragments[0].lower())
        if start != -1:
            vari["args"] = message.content[:start] + message.content[start+len(fragments[0]):]
        else:
            vari["args"] = message.content

        arguments = vari["args"].split()
        while len(arguments) < 100:
            arguments.append("")
        for ct in range(len(arguments)):
            vari[f"args{ct}"] = arguments[ct]

    if "{random}" in fragments[2]:
        vari["random"] = orderrandom()

    if "inc_var" in fragments[3:]:
        db["vars"].setdefault(fragments[0], 0)
        db["vars"][fragments[0]] += 1
        save_db(message.guild.id, db)
    if "inc_var_user" in fragments[3:]:
        var = db["var_by_user"][str(message.author.id)].setdefault(fragments[0], 0)
        db["var_by_user"][str(message.author.id)][fragments[0]] += 1
        save_db(message.guild.id, db)
    if "dec_var" in fragments[3:]:
        db["vars"].setdefault(fragments[0], 0)
        db["vars"][fragments[0]] -= 1
        save_db(message.guild.id, db)
    if "dec_var_user" in fragments[3:]:
        var = db["var_by_user"][str(message.author.id)].setdefault(fragments[0], 0)
        db["var_by_user"][str(message.author.id)][fragments[0]] -= 1
        save_db(message.guild.id, db)

    for arg in fragments[3:]:
        if arg.startswith("inc_var_"):
            var = arg[8:]
            if var:
                db["vars"].setdefault(var, 0)
                db["vars"][var] += 1
                save_db(message.guild.id, db)
        if arg.startswith("dec_var_"):
            var = arg[8:]
            if var:
                db["vars"].setdefault(var, 0)
                db["vars"][var] -= 1
                save_db(message.guild.id, db)

    if "{var}" in fragments[2]:
        vari["var"] = db["vars"].get(fragments[0], 0)
    if "{var_user}" in fragments[2]:
        vari["var_user"] = db["var_by_user"][str(message.author.id)].get(fragments[0], 0)

    for vr in db["vars"]:
        vari[f"var_{vr}"] = db["vars"][vr]

    for user in db["var_by_user"]:
        for vr in db["var_by_user"][user]:
            vari[f"var_{vr}{user}"] = db["var_by_user"][user][vr]
            if user == str(message.author.id):
                vari[f"var_{vr}_user"] = db["var_by_user"][user][vr]

    for varb in vari:
        response = response.replace(("{"+varb+"}"),str(vari[varb]))

    if len(fragments) == 3:
        if response:
            await message.channel.send(response)
    else:
        if "react" in fragments[3:]:
            try:
                if response:
                    await message.add_reaction(response.strip())
            except Exception as e:
                print(e)
        elif "replyping" in fragments[3:]:
            if response:
                weeou = await message.reply(response)
        elif "reply" in fragments[3:]:
            if response:
                weeou = await message.reply(response, allowed_mentions=discord.AllowedMentions.none())
        else:
            if response:
                weeou = await message.channel.send(response)
        if "delete" in fragments[3:]:
            if weeou or not response:
                await message.delete()
                await asyncio.sleep(5)
                if weeou:
                    await weeou.delete()
            else:
                await asyncio.sleep(5)
                await message.delete()
        elif "remove" in fragments[3:]:
            if weeou or not response:
                await message.delete()
            else:
                await asyncio.sleep(5)
                await message.delete()

def generatetaglist(guildId, tage: int = 10, merge: bool = False):
        db = load_db(guildId, merge)
        tagslist = ""
        idno = tage-10
        for tag in db["tags"][tage-10:tage]:
            if len(str(idno+10)) > len(str(idno)):
                padding = " "
            else:
                padding = ""
            tagslist += f"`{padding}{idno}.` {tag}\n"
            idno += 1
        if not tagslist:
            tagslist = "-# dust"
        embed = discord.Embed(
            title=f"Page ({math.floor(tage/10)}/{math.ceil(len(db['tags'])/10)})",
            description=tagslist,
            color=discord.Color.from_rgb(0x46, 0x78, 0x52)
        )
        return embed

def hash_string(s: str) -> int:
    h = 0x1337C0DE

    for i, ch in enumerate(s):
        char = ord(ch)

        # light index-based scrambling
        char ^= (i << (i % 5))
        char += int(math.sin(i + char) * 1000)

        # mix into hash
        h ^= char + (h << 5) - (h >> 2)
        h += (char * 31337) if i % 3 == 0 else char

        # keep hash bounded (optional but sensible)
        h &= 0xFFFFFFFFFFFFFFFF  # 64-bit wrap

    # final avalanche
    h ^= h >> 33
    h *= 0xff51afd7ed558ccd
    h ^= h >> 33
    h *= 0xc4ceb9fe1a85ec53
    h ^= h >> 33

    return h & 0xFFFFFFFFFFFFFFFF

def sanitycheck(x):
    if x == x:
        return True
    else:
        raise Exception("what the fuck")

async def load_snapins():
    for file in os.listdir("./snapins"):
        if file.endswith(".py"):
            await bot.load_extension(f"snapins.{file[:-3]}")
            snapins.append(file[:-3])
    print(f"loaded snapins: {' '.join(snapins)}")
    return True

async def kreisiday():
    print("New Day! Time to Add Debt and Give Interest!")
    onlyfiles = [f for f in listdir("tags/") if isfile(join("tags/", f))]
    for server in onlyfiles:
        guild_id = server.replace(".json", "")
        db = load_db(guild_id)
        if "invs" in db:
            for user in db["invs"]:
                if "bank" in db["invs"][user]:
                    if db["invs"][user]["bank"] > 0:
                        db["invs"][user]["bank"] = int(math.floor(db["invs"][user]["bank"]*1.0342))
                    else:
                        db["invs"][user]["bank"] = round(db["invs"][user]["bank"]*1.1)
            if "logchannel" in db:
                channel = bot.get_channel(db["logchannel"])
                if channel:
                    await channel.send("Kreisi Bank: Debt and Savings have been interested")
            save_db(guild_id, db)

async def changestatus():
    await bot.change_presence(activity=discord.CustomActivity(name=random.choice(cfg["statuses"])))

async def marischeduler(maritasks: dict, timezone: str = "UTC"):
    global mariqueue
    while True:
        now = datetime.now(tz=ZoneInfo(timezone))
        for task in maritasks:
            mariqueue.setdefault(task, 0)
            if not mariqueue[task] == 0:
                continue
            if not "hour" in maritasks[task]:
                print("task is missing hour")
                return
            if not "minute" in maritasks[task]:
                print("task is missing minute")
                return
            if not "function" in maritasks[task]:
                print("task is missing function")
                return
            if now.hour == maritasks[task]["hour"]:
                if now.minute == maritasks[task]["minute"]:
                    print(f"minute matches! executing task {task}...")
                    await maritasks[task]["function"]()
                    mariqueue[task] = 60 # prevents retriggering
        for task in mariqueue:
            if mariqueue[task] > 0:
                mariqueue[task] -= 1
        await asyncio.sleep(5)

# --- events --- #

@bot.event
async def on_ready():
    global snaps
    if not snaps:
        snaps = await load_snapins()

        await bot.add_cog(Kreisicoins(bot))
        await bot.add_cog(TagCmd(bot))
        await bot.tree.sync() #<- disabled because commands are registered by unimeter classic (not disabled anymore)
        await changestatus() # changes status
        print("Unimeter: Rewritten Source Code logged in!")
        startup = bot.get_channel(int(cfg["startupMessageChannel"]))
        await startup.send(random.choice(cfg["startupMessages"]))

        maritasks = {}
        # change status every 6 hours, at 0:00 UTC, 6:00 UTC, 12:00 UTC, and 18:00 UTC
        for hour in [0, 6, 12, 18]:
            maritasks[f"statuschange{hour}"] = {
                "hour": hour,
                "minute": 0,
                "function": changestatus
            }
        maritasks["kreisiday"] = {
            "hour": 0,
            "minute": 0,
            "function": kreisiday # defines bank function
        }
        await marischeduler(maritasks)

@bot.event
async def on_message(message: discord.Message):
    global cfg
    if message.author.id == bot.user.id:
        return
    if str(message.author.id) in cfg["blockedUsers"]:
        return
    if message.author.bot and not str(message.author.id) in cfg["allowedBots"]:
        return

    movement = False
    db = load_db(message.guild.id)
    globalse = load_db("GLOBAL")
    globalse.setdefault("ropl", {})

    for userid in globalse["ropl"]:
        if not message.author.id == 986132157967761408:
            if any(user.id == int(userid) for user in message.mentions):
                try:
                    await message.add_reaction(globalse["ropl"][userid])
                except Exception as e:
                    print(f"failed to react {globalse['ropl'][userid]}: {e}")

    merge = (str(message.guild.id) in cfg["slinxianServers"])
    db.setdefault("tags", [])
    if message.content.lower() == "unimeter":
        await message.channel.send("Unimeter: RSC is here!!!")

    cmdpref = None
    for word in prefwords:
        if message.content.lower().startswith(word):
            splitlen = len(word)
            cmdpref = message.content[splitlen:]
            movement = True
            break

    if movement:
        if cmdpref.lower().startswith("add tag "):
            if not str(message.author.id) in cfg["allowedModuleEditors"] and not message.author.guild_permissions.manage_guild:
                return await message.reply(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")
            tage = cmdpref[8:]
            if len(re.findall(r'(?<!\\);', tage)) < 2:
                return await message.reply(f"not enough semicolons\nformat: `keyword;detectionType;reply;args`")
            fragments = re.split(r'(?<!\\);', tage)
            fragments = [f.replace(r'\;', ';') for f in fragments]
            if not fragments[1] in detectionTypes and not fragments[1] in aliases:
                return await message.reply(f"invalid detection type <:picardia_dead:1122791287360323625>")
            if tage in db["tags"]:
                return await message.reply(f"this tag is already exist <:thubm_what:1150405177464070144>")
            await message.reply(f"added tag `{tage}` to **{message.guild}**")
            db["tags"].append(tage)
            save_db(message.guild.id, db)

        elif cmdpref.lower().startswith("list tags"):
            movement = True
            tage = cmdpref[10:]
            if tage.isdigit():
                tage = (int(tage))*10
            else:
                tage = 10
            embed = generatetaglist(str(message.guild.id), tage, merge)
            view = MenuView(str(message.guild.id), tage)
            view.message = await message.reply(embed=embed, view=view)
    
        elif cmdpref.lower().startswith("remove tag "):
            dokeywordsearch = False
            if not str(message.author.id) in cfg["allowedModuleEditors"] and not message.author.guild_permissions.manage_guild:
                return await message.reply(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")
            movement = True
            tage = cmdpref[11:]
    
            fragments = re.split(r'(?<!\\);', tage)
            fragments = [f.replace(r'\;', ';') for f in fragments]
    
            if len(fragments) == 1:
                dokeywordsearch = True
    
            if dokeywordsearch:
                tagses = []
                for tag in db["tags"]:
                    frogments = re.split(r'(?<!\\);', tag)
                    frogments = [f.replace(r'\;', ';') for f in frogments]
                    if fragments[0] == frogments[0]:
                        tagses.append(tag)
                if len(tagses) == 1:
                    tage = tagses[0]
                elif len(tagses) == 0:
                    return await message.reply(f"this tag is already lacks existance <:thubm_what:1150405177464070144>")
                else:
                    ambi = "ambiguous tag label, please specify which tag you want to delete specifically (whole tag or use remove tag_id):\n```\n"
                    for index, tag in enumerate(db["tags"]):
                        if tag in tagses:
                            ambi += f"{index}. {tag}\n"
                    ambi += "```"
                    return await message.reply(ambi[:2000])
    
            if not tage in db["tags"]:
                return await message.reply(f"this tag is already lacks existance <:thubm_what:1150405177464070144>")
    
            await message.reply(f"removed tag `{tage}` from **{message.guild}**")
            db["tags"].remove(tage)
            save_db(message.guild.id, db)
    
        elif cmdpref.lower().startswith("remove tag_id "):
            dokeywordsearch = False
            if not str(message.author.id) in cfg["allowedModuleEditors"] and not message.author.guild_permissions.manage_guild:
                return await message.reply(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")
            movement = True
            removebyid = False
            tage = cmdpref[14:]

            tages = tage.strip()
            if tages.isdigit():
                tage = int(tages)
                removebyid = True
    
            if removebyid:
                if tage > len(db["tags"])-1:
                    return await message.reply("id out of range")
                else:
                    rmtag = db["tags"].pop(tage)
                    save_db(message.guild.id, db)
                    return await message.reply(f"removed tag `{rmtag}` from **{message.guild}**")
            else:
                return await message.reply("not an integer")
    
        elif cmdpref.lower().startswith("update tag "):
            if not str(message.author.id) in cfg["allowedModuleEditors"] and not message.author.guild_permissions.manage_guild:
                return await message.reply(f"perms issue <:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882><:pointlaugh:1128309108001484882>")
            movement = True
            tage = cmdpref[11:]
            tage_new = cmdpref[11:]
    
            fragments = re.split(r'(?<!\\);', tage)
            fragments = [f.replace(r'\;', ';') for f in fragments]
    
            tagses = []
            for tag in db["tags"]:
                frogments = re.split(r'(?<!\\);', tag)
                frogments = [f.replace(r'\;', ';') for f in frogments]
                if fragments[0] == frogments[0]:
                    tagses.append(tag)
            if len(tagses) == 1:
                tage = tagses[0]
            elif len(tagses) == 0:
                return await message.reply(f"this tag is already lacks existance <:thubm_what:1150405177464070144>")
            else:
                ambi = "ambiguous tag label, please remove the tag you want to update specifically and create anew:\n```\n"
                for tag in tagses:
                    ambi += f"{tag}\n"
                ambi += "```"
                return await message.reply(ambi[:2000])
    
            await message.reply(f"updated tag `{tage}` to `{tage_new}` in **{message.guild}**")
            db["tags"][(db["tags"].index(tage))] = tage_new
            save_db(message.guild.id, db)

        elif cmdpref.lower().startswith("convert this to af2"):
            fbls = False
            legacy = False
            trans = False
            maxpalette = 95
            lineskip = 1
            args = cmdpref.split()[1:]
            if args:
                if "--findbestlineskip" in args:
                    fbls = True
                if "--legacy" in args:
                    legacy = True
                if "--transparent" in args:
                    trans = True
                for arg in args:
                    if arg.startswith("--palette="):
                        maxpalette = int(arg.replace("--palette=", ""))
                    if arg.startswith("--lineskip="):
                        lineskip = int(arg.replace("--lineskip=", ""))

            if not message.attachments:
                await message.reply("no file")
                return

            attachment = message.attachments[0]
            data = await attachment.read()

            if data is None:
                await message.reply("failed to get data")
                return

            name, ext = os.path.splitext(attachment.filename)
            ext = ext.lower()

            try:
                # APF/AF2 -> PNG
                if ext in apftool.extensions_all:
                    png_bytes = apftool.decodeany(data)

                    if png_bytes.startswith(b"GIF"):
                        ext = ".gif"
                    else:
                        ext = ".png"

                    file = discord.File(
                        io.BytesIO(png_bytes),
                        filename=name + ext
                    )

                # Image -> APF
                elif attachment.content_type and attachment.content_type.startswith("image/"):
                    apfdata = apftool.encodeaf2(data, lineskip, fbls, legacy, trans, maxpalette)
                    # encodeaf2(img: bytes, lineskip: int = 1, findbestlineskip: bool = False, legacy: bool = False, trans: bool = False, pal: int = 95):
        
                    file = discord.File(
                        io.BytesIO(apfdata.encode("utf-8")),
                        filename=name + ".af2"
                    )
        
                else:
                    await message.reply("file must be an image, .apf, or .af2")
                    return
        
                await message.reply(file=file)
            except Exception as e:
                await message.reply(f"conversion failed because of {e}")

        elif message.author.id == evaluser:
            if cmdpref.lower().startswith("print"):
                # just a simple one-line with no async (e.g. 2+3)
                # (c) lia milenakos, this code snippet is provided under the AGPL License https://github.com/milenakos/cat-bot/
    
                try:
                    await message.reply(eval(cmdpref[(len("print")):]))
                except Exception:
                    try:
                        await message.reply(traceback.format_exc())
                    except Exception:
                        pass

            elif cmdpref.lower().startswith("eval"):
                # complex eval, multi-line + async support
                # requires the full `await message.channel.send(2+3)` to get the result
                # (c) lia milenakos, this code snippet is provided under the AGPL License https://github.com/milenakos/cat-bot/

                # async def go():
                #  <stuff goes here>
                #
                # try:
                #  bot.loop.create_task(go())
                # except Exception:
                #  await message.reply(traceback.format_exc())
    
                silly_billy = cmdpref[(len("eval ")):]

                spaced = ""
                for i in silly_billy.split("\n"):
                    spaced += "  " + i + "\n"
    
                intro = "async def go(message, bot):\n try:\n"
                ending = "\n except Exception:\n  await message.reply(traceback.format_exc())\nbot.loop.create_task(go(message, bot))"
    
                complete = intro + spaced + ending
                exec(complete)
    
            elif cmdpref.lower().startswith("restart"):
                print("bot restart has been triggered...")
                await message.reply("restarting bot...")
                os.execv(sys.executable, ['python'] + sys.argv)

            elif cmdpref.lower().startswith("reload"):
                cfg = load_config()
                await message.reply("ok")

            elif cmdpref.lower().startswith("status"):
                try:
                    prompt = cmdpref[(len("status ")):]
                    await bot.change_presence(activity=discord.CustomActivity(name=prompt))
                    await message.reply(f"Status updated to: {prompt}")
                except Exception as e:
                    await message.reply(str(e))

            elif cmdpref.lower().startswith(f"test"):
                await message.reply("Unimeter isn't down!")
            else:
                movement = False

        else:
            movement = False

    if not movement:
        db = load_db(message.guild.id, merge)
        db.setdefault("tags", [])
        for tag in db["tags"]:
            fragments = re.split(r'(?<!\\);', tag)
            fragments = [f.replace(r'\;', ';') for f in fragments]
            trigger = resolvetag(message, fragments)
            if trigger:
                await resolveoutcome(message, fragments)

        if random.randint(1,100) == 1:
            db = load_db(message.guild.id)
            db.setdefault("unkreisi", [])
            db.setdefault("kreisi", [])
            if str(message.channel.id) in db["unkreisi"]:
                return
            if len(db["kreisi"]) > 0 and not str(message.channel.id) in db["kreisi"]:
                return
            db.setdefault("kcs", {})
            db["kcs"].setdefault(str(message.channel.id), 0)
            spawned = random.randint(13,58)
            db["kcs"][str(message.channel.id)] += spawned
            domore = ""
            if not db["kcs"][str(message.channel.id)] == spawned:
                domore = f"\n-# There is a total of {db['kcs'][str(message.channel.id)]} kreisicoins here now"
            await message.channel.send(f"**{spawned}** kreisicoins just appeared! type 'kreisi' to take them!{domore}")
            save_db(message.guild.id, db)
        if message.content.lower() == "kreisi":
            if message.author.id == 1030817797921583236:
                return await message.reply("get the fuck out")
            db = load_db(message.guild.id)
            db.setdefault("kcs", {})
            db["kcs"].setdefault(str(message.channel.id), 0)
            if db["kcs"][str(message.channel.id)] > 0:
                counted = db["kcs"][str(message.channel.id)]
                db.setdefault("invs", {})
                db["invs"].setdefault(str(message.author.id), {})
                db["invs"][str(message.author.id)].setdefault("kreisicoins", 0)
                db["invs"][str(message.author.id)]["kreisicoins"] += counted
                db["kcs"][str(message.channel.id)] = 0
                save_db(message.guild.id, db)
                await message.channel.send(f"**{message.author.name}** just got **{counted}** kreisicoins")
        if message.content.lower().startswith("doas "): # doas terminal
            command = message.content.lower()[5:]
            fragments = command.split()
            if not str(message.author.id) in cfg["allowedModuleEditors"]:
                return await message.reply("иди нахуй")
            if fragments[0] == "rm":
                if fragments[1].startswith("-") and "r" in fragments[1] and "f" in fragments[1]:
                    if fragments[2].startswith("/") and fragments[2].endswith("/*"):
                        userID = fragments[2][1:-2]
                        try:
                            member = await message.guild.fetch_member(int(userID))
                        except Exception:
                            return
                        removable_roles = [
                            role for role in member.roles
                            if role != message.guild.default_role
                            and role < message.guild.me.top_role
                        ]
                        await member.remove_roles(*removable_roles, reason=f"rm -rf'd by {message.author}")
                        await message.add_reaction("✅")

    #if message.content in cfg["startupMessages"]:
    #    await message.reply("https://media.discordapp.net/attachments/1163847466014220339/1276483659234410619/convert.gif")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name and payload.emoji.name == "taipinge":
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.id == bot.user.id:
            await channel.send("Every day, over 5000 picardias have to type a 5447-page essay and lose their sanity. Make that number less and save a picardia's sanity by unreacting the taipinge emoji. #TeamPicardias")

# --- whatever this is --- #

class MenuView(discord.ui.View):
    message: discord.Message | None = None

    def __init__(self, guildId: str, page: int) -> None:
        super().__init__(timeout=None)
        self.guildId = guildId
        self.page = page
        self.merge = guildId in cfg["slinxianServers"]

    # adding a component using it's decorator
    @discord.ui.button(label="<<", style=discord.ButtonStyle.gray)
    async def firs(self, inter: discord.Interaction, button: discord.ui.Button[MenuView]) -> None:
        self.page = 10
        embed = generatetaglist(self.guildId, self.page, self.merge)
        await inter.response.edit_message(embed=embed, view=self)
    @discord.ui.button(label="<", style=discord.ButtonStyle.gray)
    async def prev(self, inter: discord.Interaction, button: discord.ui.Button[MenuView]) -> None:
        self.page -= 10
        if self.page < 10:
            self.page = 10
        embed = generatetaglist(self.guildId, self.page, self.merge)
        await inter.response.edit_message(embed=embed, view=self)
    @discord.ui.button(label=">", style=discord.ButtonStyle.gray)
    async def next(self, inter: discord.Interaction, button: discord.ui.Button[MenuView]) -> None:
        db = load_db(self.guildId)
        self.page += 10
        if self.page > (math.ceil(len(db['tags'])/10))*10:
            self.page = (math.ceil(len(db['tags'])/10))*10
        embed = generatetaglist(self.guildId, self.page, self.merge)
        await inter.response.edit_message(embed=embed, view=self)
    @discord.ui.button(label=">>", style=discord.ButtonStyle.gray)
    async def last(self, inter: discord.Interaction, button: discord.ui.Button[MenuView]) -> None:
        db = load_db(self.guildId)
        self.page = (math.ceil(len(db['tags'])/10))*10
        embed = generatetaglist(self.guildId, self.page, self.merge)
        await inter.response.edit_message(embed=embed, view=self)

    # error handler for the view
    async def on_error(
        self, interaction: discord.Interaction[discord.Client], error: Exception, item: discord.ui.Item[typing.Any]
    ) -> None:
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        message = f"An error occurred while processing the interaction for {str(item)}:\n```py\n{tb}\n```"
        await interaction.response.send_message(message)

# --- login --- #
bot.run(cfg["token"])
