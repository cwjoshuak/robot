import discord
from discord.ext import commands
import os

from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

import os
MONGO_PW = os.getenv("MONGO_PW")

DISCORD_API_KEY = os.getenv("DISCORD_API_KEY")

mongo_client = MongoClient(f"mongodb+srv://root:{MONGO_PW}@course-data-f6kx1.mongodb.net/coursedb?retryWrites=true&w=majority")
db = mongo_client.coursedb
mongo_courses = db.courses

bot = commands.Bot(command_prefix='.')

initial_extensions = ['cogs.uci',
                      'cogs.owner']

for extension in initial_extensions:
    bot.load_extension(extension)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

bot.run(DISCORD_API_KEY)

