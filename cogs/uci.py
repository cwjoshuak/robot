import discord
from discord.ext import commands
import os

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from course import Course
import time

from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

MONGO_PW = os.getenv("MONGO_PW")

class UCI(commands.Cog, name='UCI Information'):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def cinfo(self, ctx, *args):
        """Displays UCI Course Info.
        Usage: `.cinfo INF 133`"""
        start_time = time.time()
        mongo_courses = self.bot.mongo_courses
        db = self.bot.db
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

    @commands.command(hidden=True)
    @commands.is_owner()
    async def addalias(self, ctx, *args):
        db = self.bot.db
        aliases = db.aliases
        contents = list(args)
        result = aliases.insert_one({'_id': contents[0].upper(), 'original': ' '.join(contents[1:]).upper()})
        await ctx.message.channel.send(f'Aliased {" ".join(contents[1:]).upper()} as {result.inserted_id}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def listaliases(self, ctx, *args):
        db = self.bot.db
        aliases = db.aliases
        await ctx.message.channel.send('```' + ''.join(str(list(aliases.find()))) + '```')

    @commands.command()
    async def links(self, ctx):
        embed = discord.Embed(title='Important Links', color=0x816E91)
        embed.add_field(name=':calendar_spiral: Academic Calendar', value='[Quarterly Academic Calendar 2020-21](https://www.reg.uci.edu/calendars/quarterly/2020-2021/quarterly20-21.html)', inline=False)

        class_planning = ['[WebSoc - Schedule of Classes](https://www.reg.uci.edu/perl/WebSoc)', '[AntAlmanac](https://www.reg.uci.edu/perl/WebSoc)', '[ZotCourse](https://zotcourse.appspot.com/)', '[Zotistics](https://www.zotistics.com)']

        school_related = ['[DegreeWorks](https://www.reg.uci.edu/access/student/degreeworks/?seg=U)', '[StudyList](https://www.reg.uci.edu/access/student/studylist/?seg=U)', '[Unofficial Transcript](https://www.reg.uci.edu/access/student/transcript/?seg=U)' ]
        embed.add_field(name=':notepad_spiral: Class Planning', value='\n'.join(class_planning))
        embed.add_field(name='<:UCI:721633549429768213> StudentAccess', value='\n'.join(school_related))

        await ctx.message.channel.send(embed=embed)

def setup(bot):
    mongo_client = MongoClient(f"mongodb+srv://root:{MONGO_PW}@course-data-f6kx1.mongodb.net/coursedb?retryWrites=true&w=majority")
    bot.db = mongo_client.coursedb
    bot.mongo_courses = bot.db.courses
    bot.add_cog(UCI(bot))
