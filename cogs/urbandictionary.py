import discord
from discord.ext import commands

import urllib.request
import urllib.parse
import json

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
        counter = 0
        embed = discord.Embed(description=data[counter]['definition'])
        embed.set_author(name=data[counter]['word'])
        embed.set_footer(f'{counter}/10')
        await ctx.message.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(UrbanDictionary(bot))