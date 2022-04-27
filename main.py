#bot.py
print("Loading...\n")
import os
import discord
import json as filereader
import random as dice
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print("Connecting...\n")
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(intents=intents,command_prefix=">")



@client.event
async def on_ready():
	#startup procedures
	print(f'{client.user} is ready for action!')

client.run(TOKEN)