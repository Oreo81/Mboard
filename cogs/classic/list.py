from datetime import *
from time import *
from discord.ext import commands
import sqlite3 
import asyncio #for timeout error

sqlconnect = sqlite3.connect('./media/db/mlist.db')
cursorsql = sqlconnect.cursor()

def get_hight_id(table): #return new id for list
    max_id = cursorsql.execute(f"SELECT IDlist FROM {table} ORDER BY IDlist DESC LIMIT 1")
    max_id = max_id.fetchall()
    if len(max_id)==0:
        return 1
    else:
        return int(max_id[0][0]) + 1

def name_alrdy_take(name_list,idadmin):
    check = cursorsql.execute(f"SELECT IDlist FROM list where name='{name_list}' and IDadmin = {idadmin}")
    check = check.fetchall()
    if len(check) == 0:
        return False
    else:
        return True

class list(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="listcreate",aliases=['lc', 'listc', 'createl'])
    async def listcreate(self,ctx,*name):
        name = str(name[0])
        id_admin = ctx.author.id
        if not name:
            await ctx.send("faut mettre un nom")
        else:
            if name_alrdy_take(name,id_admin):
                error = await ctx.send(f"Vous avez déjà une liste sous ce nom")
            else:
                hight_id = get_hight_id("list")
                iduseredit = []
                type_list = 'private' #'public'
                affiliation = 'user' #'server' 
                cursorsql.execute("INSERT INTO list VALUES (?,?,?,?,?,?)",(hight_id,id_admin,f'{iduseredit}',f'{name}',type_list,affiliation))
                creation_message = await ctx.send(f"Liste **{name}** créé.")
                sqlconnect.commit()

    @commands.command(name="listdelete",aliases=['ld', 'listd', 'deletel'])
    async def listdelete(self,ctx,*name):
        name = str(name[0])
        id_admin = ctx.author.id
        if not name:
            await ctx.send("Mettre un nom de liste [m!help]")
        else:
            if not name_alrdy_take(name,id_admin):
                error = await ctx.send(f"Vous n'avez aucune liste sous ce nom.")
            else:
                del_list_confirm = await ctx.send(f"Voulez vous vraiment supprimé la liste **{name}** ?")
                valid_reactions = [u"\u2705",u"\u274C"]
                await del_list_confirm.add_reaction(valid_reactions[0])
                await del_list_confirm.add_reaction(valid_reactions[1])
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in valid_reactions
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                
                    if str(reaction.emoji) == valid_reactions[0]:
                        cursorsql.execute("DELETE FROM list WHERE IDadmin = (?) and name = (?)",(id_admin,f'{name}'))
                        await del_list_confirm.clear_reaction(u"\u2705")
                        await del_list_confirm.clear_reaction(u"\u274C")
                        await del_list_confirm.edit(content=f"Liste **{name}** supprimé.")

                    else:
                        await del_list_confirm.clear_reaction(u"\u2705")
                        await del_list_confirm.clear_reaction(u"\u274C")
                        await del_list_confirm.edit(content="Annulé")

                except asyncio.TimeoutError: 
                        await del_list_confirm.clear_reaction(u"\u2705")
                        await del_list_confirm.clear_reaction(u"\u274C")
                        await del_list_confirm.edit(content="Annulé [Timeout]")

        
        sqlconnect.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        print('[+] cogs.classic.list')

# ============================================================================


def setup(bot):
    bot.add_cog(list(bot))        
#FIN ============================================================================