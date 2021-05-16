import calendar
import os
from datetime import date

import discord
from discord.ext import commands

import ymlHandler

errors = 0

color_lasa_blue = 0x0c2340
color_red = 0xe84b33
color_green = 0x72e02d
color_yellow = 0xffef42

bells_advisory = [
    ["1/5",      "08:15", "09:40", "85"],
    ["Advisory", "09:45", "10:35", "50"],
    ["2/6",      "10:40", "12:05", "85"],
    ["Lunch",    "12:05", "12:55", "50"],
    ["3/7",      "13:00", "14:25", "85"],
    ["4/8",      "14:30", "15:55", "85"]
]

bells_non_advisory = [
    ["1/5",      "08:15", "09:50", "95"],
    ["2/6",      "09:55", "11:30", "95"],
    ["Lunch",    "11:35", "12:35", "60"],
    ["3/7",      "12:40", "14:15", "95"],
    ["4/8",      "14:20", "15:55", "95"]
]

bells_c_day = [
    ["1",        "08:15", "09:00", "45"],
    ["2",        "09:05", "09:50", "45"],
    ["3",        "09:55", "10:40", "45"],
    ["4",        "10:45", "11:30", "45"],
    ["Lunch",    "11:35", "12:35", "60"],
    ["5",        "12:40", "13:25", "45"],
    ["6",        "13:30", "14:15", "45"],
    ["7",        "14:20", "15:05", "45"],
    ["8",        "15:10", "15:55", "45"]
]

bot = commands.Bot(command_prefix="lasa ")


@bot.event
async def on_ready():
    print(f"Username: {str(bot.user)}\nID: {bot.user.id}\nStatus: READY")
    await bot.change_presence(activity=discord.Activity(name="for academic dishonesty", type=3))


@bot.event
async def on_message(message):
    if not message.author.bot:
        if len(message.attachments) > 0 or len(message.embeds) > 0:
            await message.add_reaction("👍")
            await message.add_reaction("👎")
        if "admin abuse" in message.content.lower():
            await message.channel.send("https://tenor.com/view/onyx-ttv-mr-fox-is-here-minecraft-server-gif-19583883")
        await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    # We only want to tally errors outside the user input itself
    if not isinstance(error, commands.errors.CommandInvokeError):
        global errors
        errors += 1
    print("========================================")
    raise error.original


@bot.command(aliases=["notice", "event", "noticeboard", "notice-board", "announce", "announcement"])
async def board(ctx, *title):
    if ctx.guild.get_role(610536160338378765) in ctx.author.roles:
        # Invoker has Staff role, proceed
        title = " ".join(title)
        if title == "": title = "Announcement"

        box = discord.Embed(title="Create an Announcement",
                            description="This announcement will show up in <#615257559976247300>. Use the :vibration_mode: reaction to mention @everyone when the announcement is sent.", color=color_lasa_blue)
        box.add_field(name="Announcement Title", value=title, inline=False)
        box.add_field(
            name="Content", value="The next message you send will be set as the description of this announcement. Press :stop_sign: to cancel.", inline=False)
        bot_msg = await ctx.send(embed=box)

        # Add reactions for user options
        mention = "📳"
        cancel = "🛑"
        await bot_msg.add_reaction(cancel)
        await bot_msg.add_reaction(mention)

        # Wait until the user sends another message (if cancel reaction is set, message is simply ignored)
        description_msg = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel)
        # There should probably be a discord.Message.fetch_reactions() method but refreshing the message again works
        bot_msg = await ctx.channel.fetch_message(bot_msg.id)

        # Check the message reactions (sort of gross)
        cancel_flag = False
        important_flag = False
        for r in bot_msg.reactions:
            if str(r.emoji) == cancel:
                users = await r.users().flatten()
                if ctx.author in users:
                    cancel_flag = True
                    continue
            elif str(r.emoji) == mention:
                users = await r.users().flatten()
                if ctx.author in users:
                    important_flag = True
                    continue
        
        if not cancel_flag:
            # User wants to proceed; send announcement
            box = discord.Embed(title=title, description=description_msg.content, color=color_lasa_blue)
            box.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            noticeboard = bot.get_channel(615257559976247300)
            if important_flag:
                # Mention @everyone in addition to sending the announcement
                await noticeboard.send("@everyone", embed=box)
            else:
                # Do not mention @everyone
                await noticeboard.send(embed=box)
            await ctx.send(embed=discord.Embed(title="Announcement posted.", color=color_green))
    else:
        await ctx.send(embed=discord.Embed(title="Must be a staff member to post server announcements.", color=color_red))


@bot.command(aliases=["bells"])
async def bell(ctx, version="today", *args):

    def add_block_fields(embed: discord.Embed, blocks: list):
        for block in blocks:
            embed.add_field(name=block[0], value=f"`{block[1]} - {block[2]} ({block[3]})`", inline=False)

    version += " ".join(args)

    # Account for next/previous day by adding offset during autoselect
    if version.lower() in ["tomorrow", "next"]:
        day_offset = 1
        version = "today"
    elif version.lower() in ["yesterday", "last", "previous"]:
        day_offset = -1
        version = "today"
    else:
        day_offset = 0
    
    autoselect_flag = False
    if version.lower() in ["today", "now", "current"] or version.title() in calendar.day_name:
        # Autoselect a bell schedule according a normal week
        if version.title() in calendar.day_name:
            day = list(calendar.day_name).index(version.title())
        else:
            day = (date.today().weekday() + day_offset) % 7
            autoselect_flag = True
        if day in [5, 6]:
            # Saturday, Sunday
            box = discord.Embed(title="No bell schedule found for this day.", color=color_red)
            await ctx.send(embed=box)
            return
        elif day in [1, 2]:
            # Tuesday, Wednesday
            version = "advisory"
        else:
            # Monday, Thursday, (Friday)
            version = "non-advisory"

    if version.lower() in ["adv", "advisory"]:
        # Advisory schedule (can be autoselected)
        if autoselect_flag:
            box = discord.Embed(title=f"{calendar.day_name[day]} Bell Schedule - Advisory", color=color_lasa_blue)
        else:
            box = discord.Embed(title="Bell Schedule - Advisory", color=color_lasa_blue)
        add_block_fields(box, bells_advisory)
        if autoselect_flag:
            # Some weeks are exceptional to the regular schedule
            box.set_footer(text="Make sure to verify that this is the schedule being used!")

    elif version.lower() in ["reg", "norm", "regular", "normal", "nonadv", "non-adv", "nonadvisory", "non-advisory"]:
        # Regular schedule (can be autoselected)
        if autoselect_flag:
            box = discord.Embed(title=f"{calendar.day_name[day]} Bell Schedule - Non-Advisory", color=color_lasa_blue)
        else:
            box = discord.Embed(title="Bell Schedule - Non-Advisory", color=color_lasa_blue)
        add_block_fields(box, bells_non_advisory)
        if autoselect_flag:
            # Some weeks are exceptional to the regular schedule
            box.set_footer(text="Make sure to verify that this is the schedule being used!")

    elif version.lower() in ["c", "cday", "c-day"]:
        # C day schedule (all 8 periods, never autoselected as it rarely happens)
        box = discord.Embed(title="Bell Schedule - C Day", color=color_lasa_blue)
        add_block_fields(box, bells_c_day)

    else:
        box = discord.Embed(title="Unknown bell schedule.", color=color_red)

    await ctx.send(embed=box)


@bot.command(aliases=["schedules"])
async def schedule(ctx, cmd, *args):
    if cmd.lower() in ["optout", "opt-out"]:
        pass  # TODO: Opt out of the schedule function
    elif cmd.lower() in ["optin", "opt-in", "opt"]:
        pass  # TODO: Opt in the schedule function
    else:
        box = discord.Embed(title="Unknown schedule function.", color=color_red)
        # TODO: Shift down a tab once above functions filled in
        await ctx.send(embed=box)

#This is the code to do the mock command
@bot.command()
async def mock(ctx, *, arg1=None):
    messages = await ctx.channel.history(limit=2).flatten()
    print(messages)
    await ctx.message.delete()
    contextMessage = messages[1]
    messageMentions =contextMessage.mentions
    print(messageMentions)
    if arg1 == None:
        counter = 0
        newMessage = ''
        mockMessage = messages[1].content.upper()
        mockMessage = discord.utils.escape_mentions(mockMessage)
        for i in mockMessage:
            if counter == 0:
                newMessage = newMessage+i.lower()
                counter = 1
            else:
                newMessage = newMessage+i
                counter = 0
        await ctx.send(newMessage)

# We probably don't want to run the bot if it's being imported in another program
if __name__ == "__main__":
    bot_token = os.getenv("TOKEN")
    if bot_token == None:
        raise OSError("'TOKEN' environment variable is not set.")
    bot.run(bot_token)  # TODO: explain in readme
