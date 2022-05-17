from discord import *
# import discord
from discord_slash import *
from discord.ext import commands

bot = commands.Bot(command_prefix="m!",intents=Intents.default())
slash = SlashCommand(bot, sync_commands = True)

key_file  = open("./media/key.txt", "r")
key_file.close()
#récuperation du token dans key.txt

#================================================================================

version = "classic"
 #slash ou classic

if version == "slash":
    bot.load_extension("cogs.slash") #version avec commandes "slash"
    # bot.load_extension("cogs.slash")
	
elif version == "classic":
    bot.load_extension("cogs.classic") #version avec commandes "classic"
    # bot.load_extension("cogs.classic")

#================================================================================

@bot.event
async def on_ready():
	print("OK//")

bot.run(key_file.readline())
#FIN ============================================================================