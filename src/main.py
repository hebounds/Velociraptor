import calendar
import os
from datetime import date

import asyncio
import discord
from discord.ext import commands

import ymlHandler

errors = 0

color_lasa_blue = 0x0c2340
color_red = 0xe84b33
color_green = 0x72e02d
color_yellow = 0xffef42

bells_advisory = [
    ["1/5",      "8:15 am", "9:40 am", "85"],
    ["Advisory", "9:45 am", "10:35 am", "50"],
    ["2/6",      "10:40 am", "12:05 pm", "85"],
    ["Lunch",    "12:05 pm", "12:55 pm", "50"],
    ["3/7",      "1:00 pm", "2:25 pm", "85"],
    ["4/8",      "2:30 pm", "3:55 pm", "85"]
]

bells_non_advisory = [
    ["1/5",      "8:15 am", "9:50 am", "95"],
    ["2/6",      "9:55 am", "11:30 am", "95"],
    ["Lunch",    "11:35 am", "12:35 pm", "60"],
    ["3/7",      "12:40 pm", "2:15 pm", "95"],
    ["4/8",      "2:20 pm", "3:55 pm", "95"]
]

bells_c_day = [
    ["1",        "8:15 am", "9:00 am", "45"],
    ["2",        "9:05 am", "9:50 am", "45"],
    ["3",        "9:55 am", "10:40 am", "45"],
    ["4",        "10:45 am", "11:30 am", "45"],
    ["Lunch",    "11:35 am", "12:35 pm", "60"],
    ["5",        "12:40 pm", "1:25 pm", "45"],
    ["6",        "1:30 pm", "2:15 pm", "45"],
    ["7",        "2:20 pm", "3:05 pm", "45"],
    ["8",        "3:10 pm", "3:55 pm", "45"]
]

bot = commands.Bot(command_prefix="lasa ")


@bot.event
async def on_ready():
    print(f"Username: {str(bot.user)}\nID: {bot.user.id}\nStatus: READY")
    await bot.change_presence(activity=discord.Activity(name="for academic dishonesty", type=3))


@bot.event
async def on_message(message):
    if not message.author.bot:
        await bot.process_commands(message)
        await asyncio.sleep(0.5)
        message = await message.channel.fetch_message(message.id)
        if (len(message.attachments) > 0 or len(message.embeds) > 0) and message.channel.id == 615257900138496008:
            await message.add_reaction("👍")
            await message.add_reaction("👎")


#@bot.event
#async def on_command_error(ctx, error):
#    # We only want to tally errors outside the user input itself
#    if not isinstance(error, commands.errors.CommandInvokeError):
#        global errors
#        errors += 1
#    print("========================================")
#    raise error.original


@bot.command(aliases=["notice", "event", "noticeboard", "notice-board", "announce", "announcement"])
async def board(ctx, *title):
    if ctx.guild.get_role(610536160338378765) in ctx.author.roles:
        # Invoker has Staff role, proceed
        title = " ".join(title)
        if title == "":
            title = "Announcement"

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


#@bot.command(aliases=["schedules"])
#async def schedule(ctx, cmd, *args):
#    if cmd.lower() in ["optout", "opt-out"]:
#        pass  # TODO: Opt out of the schedule function
#    elif cmd.lower() in ["optin", "opt-in", "opt"]:
#        pass  # TODO: Opt in the schedule function
#    else:
#        box = discord.Embed(title="Unknown schedule function.", color=color_red)
#    await ctx.send(embed=box)


@bot.command(aliases=["tilt"])
async def mock(ctx, *, text=""):

    def fix_mentions(text, msg):
        # Make user and role mentions more readable (ignores @everyone and @here because it alternates the case anyway)
        for user in msg.mentions:
            escape = "@" + user.display_name
            text = text.replace(f"<@{user.id}>", escape)
            text = text.replace(f"<@!{user.id}>", escape)
        for role in msg.role_mentions:
            escape = "@" + role.name
            text = text.replace(f"<@&{role.id}>", escape)
        return text

    if text.strip() == "":
        source_msgs = await ctx.channel.history(limit=2).flatten()  # Grab second-to-last message in channel history
        source_text = fix_mentions(source_msgs[1].content, source_msgs[1])
        await ctx.message.delete()
    else:
        source_text = fix_mentions(text.strip(), ctx.message)
    
    result_text = ""
    for i, char in enumerate(source_text):
        # Even character index -> lowercase, odd character index -> uppercase (starting at 0)
        if i % 2 == 0:
            result_text += char.lower()
        else:
            result_text += char.upper()
    await ctx.send(result_text)


# We probably don't want to run the bot if it's being imported in another program
if __name__ == "__main__":
    bot_token = os.getenv("TOKEN")
    if bot_token == None:
        raise OSError("'TOKEN' environment variable is not set.")
    bot.run(bot_token)  # TODO: explain in readme
