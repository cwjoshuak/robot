import discord
from discord.ext import commands
import os

from dotenv import load_dotenv


import os
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='Run in DEVELOPMENT mode.')
parser.add_argument('--develop', action='store_true', help='Use development environment variables')

args = parser.parse_args()
if args.develop:
    load_dotenv(dotenv_path=Path('./.env.dev'))
else:
    load_dotenv(dotenv_path=Path('./.env.prod'))

DISCORD_API_KEY = os.getenv("DISCORD_API_KEY")

bot = commands.Bot(command_prefix='.')

initial_extensions = ['cogs.uci',
                'cogs.urbandictionary',
                      'cogs.owner']

for extension in initial_extensions:
    bot.load_extension(extension)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

bot.run(DISCORD_API_KEY)

