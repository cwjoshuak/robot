import discord
import os

from course import Course
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

import os
MONGO_PW = os.getenv("MONGO_PW")

DISCORD_API_KEY = os.getenv("DISCORD_API_KEY")

client = MongoClient(f"mongodb+srv://root:{MONGO_PW}@course-data-f6kx1.mongodb.net/coursedb?retryWrites=true&w=majority")
db = client.coursedb
mongo_courses = db.courses

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('.ping'):
        await message.channel.send('Pong!')

    if message.content.startswith('.cinfo'):
        whole_course = [i.upper() for i in message.content.split(' ') if i != '']

        if 3 <= len(whole_course) <= 4:
            dept_name = whole_course[1]
            course_number = whole_course[2]

            if len(whole_course) == 4:
                dept_name = ' '.join(whole_course[1:3])
                course_number = whole_course[3]

            course_dict = mongo_courses.find_one({'_id': dept_name})
            if course_dict is None:
                alias = db.aliases.find_one({'_id': dept_name})
                if alias is not None:
                    dept_name = alias['original']
                    course_dict = mongo_courses.find_one({'_id': dept_name})

            if course_dict is not None and course_number in course_dict:
                course = Course.from_dict(dept_name, course_dict[course_number])

                embed = course.to_embed()
                
                await message.channel.send(embed=embed)
        
    if message.content.startswith('.addalias'):
        aliases = db.aliases
        contents = message.content.split(' ')
        result = aliases.insert_one({'_id': contents[1].upper(), 'original': ' '.join(contents[2:]).upper()})
        await message.channel.send(f'Aliased {" ".join(contents[2:]).upper()} as {result.inserted_id}')

    if message.content.startswith('.listaliases'):
        aliases = db.aliases
        await message.channel.send('```' + ''.join(str(list(aliases.find()))) + '```')
client.run(DISCORD_API_KEY)