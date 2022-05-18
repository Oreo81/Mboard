from datetime import *
from time import *
from discord.ext import commands

class help(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="help",aliases=['h', '?'])
    @commands.guild_only()
    async def help(self,ctx,*input):
        await ctx.send("help")

    @commands.Cog.listener()
    async def on_ready(self):
        print('[+] cogs.classic.help')

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(help(bot))        

#FIN ============================================================================