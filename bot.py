import discord
from discord.ext import commands
import os

import time

from course import Course
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

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def cinfo(ctx, *args):
    start_time = time.time()

    whole_course = [i.upper() for i in list(args) if i != '']

    if 2 <= len(whole_course) <= 3:
        dept_name = whole_course[0]
        course_number = whole_course[1]

        if len(whole_course) == 3:
            dept_name = ' '.join(whole_course[0:2])
            course_number = whole_course[2]

        course_dict = mongo_courses.find_one({'_id': dept_name})
        if course_dict is None:
            alias = db.aliases.find_one({'_id': dept_name})
            if alias is not None:
                dept_name = alias['original']
                course_dict = mongo_courses.find_one({'_id': dept_name})

        if course_dict is not None and course_number in course_dict:
            course = Course.from_dict(dept_name, course_dict[course_number])

            embed = course.to_embed()
            elapsed_time = time.time() - start_time
            embed.set_footer(text=f'Processed in {elapsed_time}s')
            await ctx.message.channel.send(embed=embed)
    else:
        await ctx.message.channel.send(f'{" ".join(list(args))} couldn\'t be found.')

@bot.command()
@commands.is_owner()
async def addalias(ctx, *args):
    aliases = db.aliases
    contents = list(args)
    result = aliases.insert_one({'_id': contents[0].upper(), 'original': ' '.join(contents[1:]).upper()})
    await ctx.message.channel.send(f'Aliased {" ".join(contents[1:]).upper()} as {result.inserted_id}')

@bot.command()
@commands.is_owner()
async def listaliases(ctx, *args):
    aliases = db.aliases
    await ctx.message.channel.send('```' + ''.join(str(list(aliases.find()))) + '```')

@bot.command()
async def links(ctx):
    embed = discord.Embed(title='Important Links', color=0x816E91)
    embed.add_field(name=':calendar_spiral: Quarterly Academic Calendar 2020-21', value='https://www.reg.uci.edu/calendars/quarterly/2020-2021/quarterly20-21.html')
    await ctx.message.channel.send(embed=embed)
    
bot.run(DISCORD_API_KEY)