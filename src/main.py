import discord
from discord.ext import commands
import os
from datetime import date
import calendar
import ymlHandler

errors = 0

color_lasa_blue = 0x0c2340
color_red = 0xe84b33
color_green = 0x72e02d
color_yellow = 0xffef42

bot = commands.Bot(command_prefix="lasa ")


@bot.event
async def on_ready():
    print(f"Username: {str(bot.user)}\nID: {bot.user.id}\nStatus: READY")
    await bot.change_presence(activity=discord.Activity(name="for academic dishonesty", type=3))


@bot.event
async def on_message(message):
    if not message.author.bot: # 
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
        title = " ".join(title)
        if title == "": title = "Announcement"
        
        box = discord.Embed(title="Create an Announcement", description="This announcement will show up in <#615257559976247300>. Use the :vibration_mode: reaction to mention @everyone when the announcement is sent.", color=color_lasa_blue)
        box.add_field(name="Announcement Title", value=title, inline=False)
        box.add_field(name="Content", value="The next message you send will be set as the description of this announcement. Press :stop_sign: to cancel.", inline=False)
        bot_msg = await ctx.send(embed=box)
        
        mention = "📳"
        cancel = "🛑"
        await bot_msg.add_reaction(cancel)
        await bot_msg.add_reaction(mention)
        
        description_msg = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel)
        bot_msg = await ctx.channel.fetch_message(bot_msg.id) # There should probably be a discord.Message.fetch_reactions() method but this works too
        
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
            box = discord.Embed(title=title, description=description_msg.content, color=color_lasa_blue)
            box.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            noticeboard = bot.get_channel(615257559976247300)
            if important_flag:
                await noticeboard.send("@everyone", embed=box)
            else:
                await noticeboard.send(embed=box)
            await ctx.send(embed=discord.Embed(title="Announcement posted.", color=color_green))
    else:
        await ctx.send(embed=discord.Embed(title="Must be a staff member to post server announcements.", color=color_red))


@bot.command(aliases=["bells"])
async def bell(ctx, version="today", *args):
    version += " ".join(args)
    
    if version.lower() in ["tomorrow", "next"]:
        day_offset = 1
        version = "today"
    elif version.lower() in ["yesterday", "last", "previous"]:
        day_offset = -1
        version = "today"
    else:
        day_offset = 0
    
    autoselect_flag = False
    if version.lower() in ["today", "now", "current"]:
        autoselect_flag = True
        day = (date.today().weekday() + day_offset) % 7
        if day in [5, 6]: # Weekend
            box = discord.Embed(title="No bell schedule found for this day.", color=color_red)
            await ctx.send(embed=box)
            return
        elif day in [1, 2]: # Tue/Wed (advisory)
            version = "advisory"
        else: # Non-advisory
            version = "non-advisory"
    
    if version.lower() in ["adv", "advisory"]:
        box = discord.Embed(title=(f"{calendar.day_name[day]} Bell Schedule - Advisory" if autoselect_flag else "Bell Schedule - Advisory"), color=color_lasa_blue)
        box.add_field(name="Period 1/5", value="8:15 am - 9:40 am (85)", inline=False)
        box.add_field(name="Advisory", value="9:45 am - 10:35 am (50)", inline=False)
        box.add_field(name="Period 2/6", value="10:40 am - 12:05 pm (85)", inline=False)
        box.add_field(name="Lunch", value="12:05 pm - 12:55 pm (50)", inline=False)
        box.add_field(name="Period 3/7", value="1:00 pm - 2:25 pm (85)", inline=False)
        box.add_field(name="Period 4/8", value="2:30 pm - 3:55 pm (85)", inline=False)
        if autoselect_flag: box.set_footer(text="Make sure to verify that this is the schedule being used!") # Schedule is autoselected by weekday, exceptions not taken into account
    
    elif version.lower() in ["reg", "norm", "regular", "normal", "nonadv", "non-adv", "nonadvisory", "non-advisory"]:
        box = discord.Embed(title=(f"{calendar.day_name[day]} Bell Schedule - Non-Advisory" if autoselect_flag else "Bell Schedule - Non-Advisory"), color=color_lasa_blue)
        box.add_field(name="Period 1/5", value="8:15 am - 9:50 am (95)", inline=False)
        box.add_field(name="Period 2/6", value="9:55 am - 11:30 am (95)", inline=False)
        box.add_field(name="Lunch", value="11:35 am - 12:35 pm (60)", inline=False)
        box.add_field(name="Period 3/7", value="12:40 pm - 2:15 pm (95)", inline=False)
        box.add_field(name="Period 4/8", value="2:20 pm - 3:55 pm (95)", inline=False)
        if autoselect_flag: box.set_footer(text="Make sure to verify that this is the schedule being used!") # Same reason as above
    
    elif version.lower() in ["c", "cday", "c-day"]:
        box = discord.Embed(title="Bell Schedule - C Day", color=color_lasa_blue)
        box.add_field(name="Period 1", value="8:15 am - 9:00 am (45)", inline=False)
        box.add_field(name="Period 2", value="9:05 am - 9:50 am (45)", inline=False)
        box.add_field(name="Period 3", value="9:55 am - 10:40 am (45)", inline=False)
        box.add_field(name="Period 4", value="10:45 am - 11:30 am (45)", inline=False)
        box.add_field(name="Lunch", value="11:35 am - 12:35 pm (60)", inline=False)
        box.add_field(name="Period 5", value="12:40 pm - 1:25 pm (45)", inline=False)
        box.add_field(name="Period 6", value="1:30 pm - 2:15 pm (45)", inline=False)
        box.add_field(name="Period 7", value="2:20 pm - 3:05 pm (45)", inline=False)
        box.add_field(name="Period 8", value="3:10 pm - 3:55 pm (45)", inline=False)
        # C day schedule will never be autoselected
    
    else:
        box = discord.Embed(title="Unknown bell schedule.", color=color_red)
    
    await ctx.send(embed=box)


@bot.command(aliases=["schedules"])
async def schedule(ctx, cmd, *args):
    if cmd.lower() in ["optout", "opt-out"]:
        pass # Opt out of the schedule function
    elif cmd.lower() in ["optin", "opt-in", "opt"]:
        pass # Opt in the schedule function
    else:
        box = discord.Embed(title="Unknown schedule function.", color=color_red)
        await ctx.send(embed=box) # Shift down a tab once above functions filled in


# We probably don't want to run the bot if it's being imported in another program
if __name__ == "__main__":
    bot.run(os.getenv("TOKEN")) # details in the README
