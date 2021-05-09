import discord
import os

client = discord.Client()

@client.event
async def on_message(message):
    if message.content.startswith('lasa schedule optout'):
        await message.channel.send(message.user + 'is now opted out!')

client.run(os.getenv('TOKEN'))