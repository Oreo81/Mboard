from discord import *
# import discord
from discord_slash import *
from discord.ext import commands

bot = commands.Bot(command_prefix="m!",intents=Intents.default())
slash = SlashCommand(bot, sync_commands = True)

key_file  = open("./media/key.txt", "r")

#récuperation du token dans key.txt

#================================================================================

version = "classic"
 #slash ou classic

if version == "slash": #version avec commandes "slash"
    bot.load_extension("cogs.slash") 
    # bot.load_extension("cogs.slash")
	
elif version == "classic": #version avec commandes "classic"
    bot.load_extension("cogs.classic.list") 
    bot.load_extension("cogs.classic.help") 
    # bot.load_extension("cogs.classic")

#================================================================================

@bot.event
async def on_ready():
	print("[+] main")

bot.run(key_file.readline())
key_file.close()
#FIN ============================================================================