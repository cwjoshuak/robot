import discord
from discord import Colour
from discord.ext import commands

import urllib.request
import urllib.parse
import json
import asyncio

class UrbanDictionary(commands.Cog):
    BASE_URL = 'http://api.urbandictionary.com/v0/define?'
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ud(self, ctx, *args, member: discord.Member = None):
        member = member or ctx.author
        url = self.BASE_URL + urllib.parse.urlencode({'term': ' '.join(args)})
        
        request = urllib.request.urlopen(url)
        data = json.load(request)
        data = data['list']
        if len(data) > 0:
            counter = 0
            embed = discord.Embed(description=data[counter]['definition'], colour=Colour.dark_teal())
            embed.set_author(name=data[counter]['word'])
            embed.set_footer(text=f'{counter+1} / {len(data)}')
            sent_msg = await ctx.message.channel.send(embed=embed)
            if len(data) > 1:
                await sent_msg.add_reaction('⬅️')
                await sent_msg.add_reaction('➡️')

                def check(reaction, user):
                    return user == ctx.message.author and reaction.message.id == sent_msg.id and reaction.emoji in ['⬅️', '➡️']
                try:
                    while True:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
                        if reaction.emoji == '⬅️':
                            if counter-1 >= min(0, len(data)):
                                counter -= 1
                                embed.description = data[counter]['definition']
                                embed.set_footer(text=f'{counter+1} / {len(data)}')
                                await sent_msg.edit(embed=embed)
                                
                        elif reaction.emoji == '➡️':
                            if counter+1 < min(10, len(data)):
                                counter += 1
                                embed.description = data[counter]['definition']
                                embed.set_footer(text=f'{counter+1} / {len(data)}')
                                await sent_msg.edit(embed=embed)
                        for r in reaction.message.reactions:
                            async for usr in r.users():
                                if not usr.bot:
                                    await r.remove(usr)
                except asyncio.TimeoutError:
                    await sent_msg.clear_reactions()
        else:
            embed = discord.Embed(description=f"**{member.name}#{member.discriminator}** Couldn't find definition for that term.", colour=Colour.from_rgb(238, 38, 32))
            await ctx.message.channel.send(embed=embed)

            

def setup(bot):
    bot.add_cog(UrbanDictionary(bot))