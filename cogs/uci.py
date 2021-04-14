import discord
from discord.ext import commands
from discord.utils import get

import os

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from course import Course
from cryptography.fernet import Fernet
import time
import re
from datetime import datetime
import pytz
import asyncio

from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

MONGO_PW = os.getenv("MONGO_PW")
MOD_CONFESSIONS_CHANNEL = int(os.getenv("MOD_CONFESSIONS_CHANNEL"))
PUBLIC_CONFESSIONS_CHANNEL = int(os.getenv("PUBLIC_CONFESSIONS_CHANNEL"))
CAFE_QUESTIONS_CHANNEL = int(os.getenv("CAFE_QUESTIONS_CHANNEL"))
FERNET_KEY = os.getenv("FERNET_KEY")

class UCI(commands.Cog, name='UCI Information'):
    def __init__(self, bot):
        self.bot = bot
        self.fernet = Fernet(FERNET_KEY)
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

        class_planning = ['[WebSoc - Schedule of Classes](https://www.reg.uci.edu/perl/WebSoc)', '[AntAlmanac](https://antalmanac.com)', '[ZotCourse](https://zotcourse.appspot.com/)', '[Zotistics](https://www.zotistics.com)']

        school_related = ['[DegreeWorks](https://www.reg.uci.edu/access/student/degreeworks/?seg=U)', '[StudyList](https://www.reg.uci.edu/access/student/studylist/?seg=U)', '[Unofficial Transcript](https://www.reg.uci.edu/access/student/transcript/?seg=U)' ]
        embed.add_field(name=':notepad_spiral: Class Planning', value='\n'.join(class_planning))
        embed.add_field(name='<:UCI:721633549429768213> StudentAccess', value='\n'.join(school_related))

        await ctx.message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        msg_list = message.clean_content.split(' ')
        first_word = msg_list[0]
        if type(message.channel) is discord.DMChannel and first_word.lower() == 'confess':
            
            mod_confession_channel = self.bot.get_channel(MOD_CONFESSIONS_CHANNEL)
            
            await message.add_reaction('👍')
            await message.channel.send('React with 👍 in 30s if you want to send this confession.')
            def check(reaction, user):
                return user == message.author and str(reaction.emoji) == '👍' and reaction.message.id == message.id
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await message.remove_reaction('👍', self.bot.user)
                await message.add_reaction('🚫')
            else:
                await reaction.message.add_reaction('📨')
                confession = ' '.join(message.clean_content.split(' ')[1:])
                embed = discord.Embed(description=confession, color=0x7bdee3)
                coded_id = self.fernet.encrypt(str.encode(f'{user.id}'))
                coded_id = coded_id.decode('ascii')
                embed.set_footer(text=f'{coded_id}')
                await mod_confession_channel.send(embed=embed)
                last_message = await mod_confession_channel.history(limit=1).flatten()
                await last_message[0].add_reaction('✅')
                await last_message[0].add_reaction('🍀')
                await last_message[0].add_reaction('🚫')
                
    
    async def confessionTitleFormat(self, channelID):
        public_confession_channel = self.bot.get_channel(PUBLIC_CONFESSIONS_CHANNEL)
        cafe_question_channel = self.bot.get_channel(CAFE_QUESTIONS_CHANNEL)

        utcmoment_naive = datetime.utcnow()
        utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
        localDatetime = utcmoment.astimezone(pytz.timezone('America/Los_Angeles'))

        embedTitleFormat = localDatetime.strftime('%a #1')

        last_message = ''
        if channelID == public_confession_channel:
            last_message = await public_confession_channel.history(limit=1).flatten()
        elif channelID == cafe_question_channel:
            last_message = await cafe_question_channel.history(limit=1).flatten()

        if len(last_message) > 0:
            try:
                next_num = int(last_message[0].embeds[0].title.split('#')[1]) + 1
                embedTitleFormat = localDatetime.strftime(f'%a #{next_num}')
                last_message_day = last_message[0].embeds[0].title.split(' ')[0]
                if last_message_day != embedTitleFormat.split(' ')[0]:
                    embedTitleFormat = localDatetime.strftime('%a #1')
            except:
                print('failed')
           
        return embedTitleFormat

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     mod_confession_channel = self.bot.get_channel(MOD_CONFESSIONS_CHANNEL)
    #     public_confession_channel = self.bot.get_channel(PUBLIC_CONFESSIONS_CHANNEL)
    #     if reaction.message.channel == mod_confession_channel and not user.bot:
    #         embedTitleFormat = await self.confessionTitleFormat()
            
    #         if reaction.emoji == '✅':
    #             embed = reaction.message.embeds[0]
    #             embed.title = embedTitleFormat
    #             await reaction.message.edit(content=f'Accepted by {user.name}\n{reaction.message.content}')
    #             reacted_users = await reaction.users().flatten()
    #             if reaction.count < 3:
    #                 await public_confession_channel.send(embed=embed)
    #                 await reaction.message.add_reaction('📨')
    #         elif reaction.emoji == '🚫':
    #             await reaction.message.edit(content=f'Rejected by {user.name}\n{reaction.message.content}')
    #             await reaction.message.add_reaction('↩️')
    #         elif reaction.emoji == '↩️':
    #             await reaction.message.edit(content=f'Reset by {user.name}\n{reaction.message.content}')
    #             await reaction.message.clear_reactions()
    #             await reaction.message.add_reaction('✅')
    #             await reaction.message.add_reaction('🚫')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        mod_confession_channel = self.bot.get_channel(MOD_CONFESSIONS_CHANNEL)
        public_confession_channel = self.bot.get_channel(PUBLIC_CONFESSIONS_CHANNEL)
        cafe_question_channel = self.bot.get_channel(CAFE_QUESTIONS_CHANNEL)

        message_channel = self.bot.get_channel(payload.channel_id)
        if message_channel == mod_confession_channel and self.bot.user.id != payload.user_id:
            message = await message_channel.fetch_message(payload.message_id)
            user = self.bot.get_user(payload.user_id)
            
            if payload.emoji.name == '✅':
                embed = message.embeds[0]
                embedTitleFormat = await self.confessionTitleFormat(public_confession_channel)
                embed.title = embedTitleFormat
                embed.set_footer(text='')
                await message.edit(content=f'Accepted by {user.name}\n{message.content}')
                message_reaction = list(filter(lambda x: x.emoji == payload.emoji.name, message.reactions))

                if len(message_reaction) > 0 and message_reaction[0].count < 3:
                    await public_confession_channel.send(embed=embed)
                    await message.add_reaction('📨')
            elif payload.emoji.name == '🍀':
                embed = message.embeds[0]
                embedTitleFormat = await self.confessionTitleFormat(cafe_question_channel)
                embed.title = embedTitleFormat
                embed.set_footer(text='')
                temp_msg = embed.description
                pattern = re.compile(r"(?<=\|)(.*)")
                matches = pattern.search(temp_msg)
                if matches is not None:
                    embed.description = matches.group(0).strip()
                await message.edit(content=f'Accepted by {user.name}\n{message.content}')
                message_reaction = list(filter(lambda x: x.emoji == payload.emoji.name, message.reactions))

                if len(message_reaction) > 0 and message_reaction[0].count < 3:
                    await cafe_question_channel.send(embed=embed)
                    await message.add_reaction('📨')
            elif payload.emoji.name == '🚫':
                await message.edit(content=f'Rejected by {user.name}\n{message.content}')
                await message.add_reaction('↩️')
            elif payload.emoji.name == '↩️':
                await message.edit(content=f'Reset by {user.name}\n{message.content}')
                await message.clear_reactions()
                await message.add_reaction('✅')
                await message.add_reaction('🍀')
                await message.add_reaction('🚫')
                


    @commands.Cog.listener()       
    async def on_member_join(self, member: discord.Member):
        if member.guild.id == 691084469762916363:
            desc = \
            f"""
            Hello **{member.display_name}**, welcome to **UCI 2024**.

            1. Read the server rules at <#703819922974834809>.

            2. Verify yourself at <#755315885131956274> to get access to the rest of the server channels.

            3. [Optional] Assign yourself a major / color at <#691085894500745257> and pronouns at <#714040116699463710>.

            I can also list course information! Try typing `.cinfo WRITING 39A` into <#693660139684757524>.

            Important links are listed below. Access them by typing `.links` into <#693587363141517403>.

            Invite your friends! Share me: https://discord.gg/uci24
            """

            embed = discord.Embed(title='', description=desc, color=0x9400D3)
            embed.add_field(name=':calendar_spiral: Academic Calendar', value='[Quarterly Academic Calendar 2020-21](https://www.reg.uci.edu/calendars/quarterly/2020-2021/quarterly20-21.html)', inline=False)

            class_planning = ['[WebSoc - Schedule of Classes](https://www.reg.uci.edu/perl/WebSoc)', '[AntAlmanac](https://antalmanac.com)', '[ZotCourse](https://zotcourse.appspot.com/)', '[Zotistics](https://www.zotistics.com)']

            school_related = ['[DegreeWorks](https://www.reg.uci.edu/access/student/degreeworks/?seg=U)', '[StudyList](https://www.reg.uci.edu/access/student/studylist/?seg=U)', '[Unofficial Transcript](https://www.reg.uci.edu/access/student/transcript/?seg=U)' ]
            embed.add_field(name=':notepad_spiral: Class Planning', value='\n'.join(class_planning))
            embed.add_field(name='<:UCI:721633549429768213> StudentAccess', value='\n'.join(school_related))

            embed.set_footer(text='')
            await member.send(embed=embed)

def setup(bot):
    mongo_client = MongoClient(f"mongodb+srv://root:{MONGO_PW}@course-data-f6kx1.mongodb.net/coursedb?retryWrites=true&w=majority")
    bot.db = mongo_client.coursedb
    bot.mongo_courses = bot.db.courses
    bot.add_cog(UCI(bot))
