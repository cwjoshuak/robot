from discord.ext import commands

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()
FERNET_KEY = os.getenv("FERNET_KEY")

class OwnerCog(commands.Cog, name="Owner Commands", command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot
        self.fernet = Fernet(FERNET_KEY)
    
    # Hidden means it won't show up on the default help.
    @commands.command(name='load')
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload')
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='rl')
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='decode')
    @commands.is_owner()
    async def decode_fernet(self, ctx, *, user_id: str):
        try:
            print(str.encode(user_id))
            id = self.fernet.decrypt(str.encode(user_id))
            id = id.decode('ascii')
            await ctx.send(id)
        except Exception:
            await ctx.send(f"Failed to decode {user_id}")
            

def setup(bot):
    bot.add_cog(OwnerCog(bot))
