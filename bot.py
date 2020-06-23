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
                      'cogs.owner']

for extension in initial_extensions:
    bot.load_extension(extension)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

# @bot.event
# async def on_message(message):
#     msg_list = message.clean_content.split(' ')
#     first_word = msg_list[0]
#     print(message, type(message.channel), first_word.lower())
#     if type(message.channel) is discord.DMChannel and first_word.lower() == 'confess':
#         confession = ' '.join(message.clean_content.split(' ')[1:])
#         confession_channel = bot.get_channel(703580865036288081)

#         embed = discord.Embed(title=f'Confession #', description=confession, color=0x7bdee3)
#         await confession_channel.send(embed=embed)
#         #724569627434418197
#     await bot.process_commands(message)

 async def on_member_join(member: discord.Member):
    if member.guild.id == 691084469762916363:
        desc = \
        f"""
        Hello **{member.display_name}**, welcome to **UCI 2024**.

        1. Read the server rules at <#703819922974834809>.

        2. Assign yourself a major at <#691085894500745257> to get access to the rest of the server channels.

        3. [Optional] Assign yourself a color at <#695439256675680295> and pronouns at <#714040116699463710>.

        I can also list course information! Try typing `.cinfo WRITING 39A` into <#693660139684757524>.

        Important links are listed below. Access them by typing `.links` into <#693587363141517403>.

        Invite your friends! Share me: https://discord.gg/65X83xU
        """

        embed = discord.Embed(title='', description=desc, color=0x9400D3)
        embed.add_field(name=':calendar_spiral: Academic Calendar', value='[Quarterly Academic Calendar 2020-21](https://www.reg.uci.edu/calendars/quarterly/2020-2021/quarterly20-21.html)', inline=False)

        class_planning = ['[WebSoc - Schedule of Classes](https://www.reg.uci.edu/perl/WebSoc)', '[AntAlmanac](https://www.reg.uci.edu/perl/WebSoc)', '[ZotCourse](https://zotcourse.appspot.com/)', '[Zotistics](https://www.zotistics.com)']

        school_related = ['[DegreeWorks](https://www.reg.uci.edu/access/student/degreeworks/?seg=U)', '[StudyList](https://www.reg.uci.edu/access/student/studylist/?seg=U)', '[Unofficial Transcript](https://www.reg.uci.edu/access/student/transcript/?seg=U)' ]
        embed.add_field(name=':notepad_spiral: Class Planning', value='\n'.join(class_planning))
        embed.add_field(name='<:UCI:721633549429768213> StudentAccess', value='\n'.join(school_related))

        embed.set_footer(text='')
        await member.send(embed=embed)

bot.run(DISCORD_API_KEY)

