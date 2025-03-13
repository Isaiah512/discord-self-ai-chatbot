"""
Discord client setup
"""
import discord
from bot.events import on_ready as handle_ready, on_message as handle_message

# Initialize Discord client
client = discord.Client()

@client.event
async def on_ready():
    await handle_ready(client)

@client.event
async def on_message(message):
    await handle_message(client, message)
