import discord
from discord.ext import commands
import os

from dotenv import load_dotenv
load_dotenv()

import os

DISCORD_API_KEY = os.getenv("DISCORD_API_KEY")

bot = commands.Bot(command_prefix='.')

initial_extensions = ['cogs.uci',
                      'cogs.owner']

for extension in initial_extensions:
    bot.load_extension(extension)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

bot.run(DISCORD_API_KEY)

