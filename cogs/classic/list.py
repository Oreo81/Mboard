from datetime import *
from hashlib import new
import time
import discord
from discord.ext import commands
import sqlite3 
import asyncio #for timeout error
import allocine as al
import sqlmovie as sq

cursorsql = sq.cursor()

#------------------------------
def displaymod(movie):
    genre = ""
    for sty in movie['style']:
        genre += sty + " / "
    genre = genre[:-2]

    ratting = ""
    for rt in movie['ratting']:
        ratting += rt + " / "
    ratting = ratting[:-2]

    embed = discord.Embed(
        title = movie['nom'],
        color = discord.Colour.from_rgb(242, 104, 24),
        url = movie['link']
    )
    embed.set_footer(text=movie['link'], icon_url = "https://c.clc2l.com/t/a/l/allocine-qy7n55.png")
    embed.set_image(url=movie['img'])
    embed.add_field(name='〉 Durée', value=movie['duree'], inline= True)
    embed.add_field(name='〉 Date', value=movie['date'], inline= True)
    embed.add_field(name='〉 Genre', value=genre, inline= False)
    embed.add_field(name='〉 Note Presse/Spectateur', value=ratting, inline= True)
    return embed

#------------------------------
def get_info(url):
    info = al.get_full_info(url)
    return info

#------------------------------
def err_display(ctx,err_message):
    error = discord.Embed(
        title = "{}  Erreur dans la commande".format("\U000026D4",ctx.message.content),
        color = discord.Colour.dark_red()
    )
    error.add_field(name=f'〉 {err_message}', value='Voir m!help', inline= False)
    return error

#------------------------------------------------------------
class list(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     error = discord.Embed(
    #         title = "{}  La commande [{}] n'existe pas".format("\U000026D4",ctx.message.content),
    #         color = discord.Colour.dark_red()
    #     )
    #     await ctx.send(embed = error)

#------------------------------
    @commands.command(name="deletelist",aliases=['dl'])
    async def listdel(self,ctx,*name):
        id_admin = ctx.author.id
        if not name:
            await ctx.send("> Mettre un nom de liste [m!help]")
        else:
            name = str(name[0])
            if not sq.name_alrdy_take(name,id_admin):
                error = await ctx.send(f"> Vous n'avez aucune liste sous ce nom.")
            else:
                del_list_confirm = await ctx.send(f"> Voulez vous vraiment supprimé la liste **{name}** ?")
                valid_reactions = [u"\u2705",u"\u274C"]
                await del_list_confirm.add_reaction(valid_reactions[0])
                await del_list_confirm.add_reaction(valid_reactions[1])
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in valid_reactions
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)    
                    if str(reaction.emoji) == valid_reactions[0]:
                        id_list = sq.get_id_list(f'{name}',id_admin)
                        cursorsql.execute("DELETE FROM list WHERE IDadmin = (?) and name = (?)",(id_admin,f'{name}'))
                        cursorsql.execute("DELETE FROM inlist WHERE IDlist = (?)",(id_list))
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
        sq.commit()





#------------------------------
    @commands.command(name="createlist",aliases=['cl'])
    async def listcreate(self,ctx,*arg):
        id_admin = ctx.author.id
        if len(arg) == 0:
            await ctx.send("> Erreur dans la commande: ")
        else:
            name = str(name[0])
            if sq.name_alrdy_take(name,id_admin):
                error = await ctx.send(f"Vous avez déjà une liste sous ce nom")
            else:
                hight_id = sq.get_hight_id("list")
                iduseredit = []
                type_list = 'private' #'public'
                affiliation = 'user' #'server' 
                cursorsql.execute("INSERT INTO list VALUES (?,?,?,?,?,?)",(hight_id,id_admin,f'{iduseredit}',f'{name}',type_list,affiliation))
                creation_message = await ctx.send(f"Liste **{name}** créé.")
        sq.commit()

#------------------------------
    @commands.command(name="listadd",aliases=['la', 'ladd'])
    async def listadd(self,ctx, *arg):
        idadmin = ctx.author.id
        if len(arg) != 2:
            # await ctx.send("> Pour rajouté un film, il faut l'id du film", file=discord.File('media/img/exemple.png'))
            await ctx.send("> Erreur dans la commande. [m!help]")
        else:
            name_list= arg[1]
            url = arg[0]
            movie_link = get_info(url)
            list_exist = sq.name_alrdy_take(name_list,idadmin)
            if list_exist:
                if not movie_link:
                    await ctx.send("> Ce film n'existe pas")
                else:
                    if sq.check_movie_in_list(url,idadmin):
                        movie_existe = cursorsql.execute(f"SELECT IDmovie FROM movie WHERE IDmovie = {url}")
                        movie_existe = movie_existe.fetchall()
                        IDlist = sq.get_id_list(name_list,idadmin)
                        if len(movie_existe)==0:
                            cursorsql.execute("INSERT INTO movie VALUES (?,?,?,?,?,?,?,?)",(movie_link['IDmovie'],f"{movie_link['nom']}",f"{movie_link['date']}",f"{movie_link['duree']}",f"{movie_link['ratting']}",f"{movie_link['img']}",f"{movie_link['style']}",f"{movie_link['link']}",))
                            cursorsql.execute("INSERT INTO inlist VALUES (?,?,?,?,?)",(IDlist,url,idadmin,0,'False'))
                            await ctx.send(f"> Ajout du film dans la list")
                        else:
                            cursorsql.execute("INSERT INTO inlist VALUES (?,?,?,?,?)",(IDlist,url,idadmin,0,'False'))
                            await ctx.send(f"> Ajout du film dans la list")
                    else:
                        await ctx.send(f"> Ce film est déjà dans la liste **{name_list}**")
            else:
                await ctx.send(f"> Vous n'avez pas de liste **{name_list}**")
            sq.commit()

#------------------------------
    @commands.command(name="listremove",aliases=['lr','lrm'])
    async def remove(self,ctx, *arg):
        idadmin = ctx.author.id
        if len(arg) != 2:
            await ctx.send("> Erreur dans la commande. [m!help]")
        else:
            IDmovie = arg[0]
            nom_list = arg[1]
            id_list = sq.get_id_list(nom_list,idadmin)
            cursorsql.execute("DELETE FROM inlist WHERE IDlist = (?) and IDmovie = (?)",(id_list,IDmovie))
            await ctx.send(f"> Le film à été enlever de la liste")
            sq.commit()

#------------------------------
    @commands.command(name="film",aliases=['f', 'movie'])
    async def film(self,ctx, *arg):
        idadmin = ctx.author.id
        if len(arg) > 1:
            await ctx.send(embed = err_display(ctx,"Il faut seulement renseigné l'ID d'un film."))
        elif len(arg) == 1:
            IDmovie = arg[0]
            movie = sq.get_info_with_id(IDmovie)
            if not movie:
                await ctx.send("> Ce film n'est pas enregistré dans la bdd")
            else:
                embed = displaymod(movie)
                await ctx.send(f"> Information: {movie['nom']} [{movie['IDmovie']}]", embed = embed)
        else:
            await ctx.send(embed = err_display(ctx,'Aucune ID de film renseigné.'))



#------------------------------
    @commands.command(name="listsee",aliases=['ls'])
    async def listsee(self,ctx, *arg):
        idadmin = ctx.author.id
        if len(arg) == 0: #si pas d'argument --> affichier les listes créer par l'utilisateur
            user_list = cursorsql.execute(f"SELECT * FROM list WHERE IDadmin = {idadmin}")
            user_list = user_list.fetchall()
            embed = discord.Embed(
                    title = 'vos liste',
                    color = discord.Colour.from_rgb(255, 255, 255),
            )
            embed.set_author(name="{} - [m!ls]".format(ctx.author.name),icon_url=ctx.author.avatar_url)
            for liste in user_list:
                movie_in_list = cursorsql.execute(f"SELECT * FROM inlist WHERE IDadmin = {idadmin} and IDlist = {liste[0]}")
                movie_in_list = movie_in_list.fetchall()
                embed.add_field(name=f'〉 {liste[3]}', value=f'Il y a {len(movie_in_list)} film(s)', inline= False)
            await ctx.send(embed = embed)

        elif len(arg) == 1:
            if sq.name_alrdy_take(arg[0],idadmin):
                id_list = sq.get_id_list(arg[0],idadmin)
                movie_in_list = cursorsql.execute(f"SELECT * FROM inlist WHERE IDadmin = {idadmin} and IDlist = {id_list}")
                movie_in_list = movie_in_list.fetchall()
                if len(movie_in_list) == 0:
                    embed.add_field(name=f'〉 Aucun film trouvé', value=f'Pour en rajouter: [m!help]', inline= False)
                else:
                    if len(movie_in_list) > 10:
                        valid_reactions = [u'\u2B05',u'\u27A1',u'\U0001F522']
                        new_list = []
                        
                        temp = -1
                        for i in range(0,len(movie_in_list)):
                            if i%10 == 0:
                                temp += 1
                                new_list.append([])
                                new_list[temp].append(movie_in_list[i])
                            else:
                                new_list[temp].append(movie_in_list[i])
                        current = 0
                        last_page = len(new_list)-1
                        valid_page = [str(x) for x in range(0,last_page+1)]

                        def display(current,last_page):
                            embed = discord.Embed(
                                title = f'~ {arg[0]} ~ Page {current}/{last_page}',
                                color = discord.Colour.from_rgb(254, 204, 0),
                                )
                            for liste in new_list[current]:
                                movie = sq.get_info_with_id(liste[1])
                                movie_name = movie['nom']
                                if liste[4] == 'True':
                                    date_vu = datetime.fromtimestamp(liste[3]).strftime('%Y-%m-%d')
                                    embed.add_field(name=f':green_square: 〉 {movie_name} | Vu le {date_vu}', value=f'ID: {liste[1]}', inline= False)
                                else:
                                    embed.add_field(name=f':red_square: 〉 {movie_name}', value=f'ID: {liste[1]}', inline= False)
                            
                            return embed

                        show = await ctx.send(embed = display(current,last_page))
                        await show.add_reaction(valid_reactions[1])
                        await show.add_reaction(valid_reactions[2])
                        def check(reaction, user):
                            return user == ctx.author and str(reaction.emoji) in valid_reactions
                        try:
                            while True:
                                timeout = 1
                                # reaction = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)    
                                reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)    
                                if str(reaction.emoji) == valid_reactions[0]:
                                    current -= 1
                                    await show.delete()
                                    show = await ctx.send(embed = display(current,last_page))
                                    if current == 0:
                                        await show.add_reaction(valid_reactions[1])
                                    elif current == last_page:
                                        await show.add_reaction(valid_reactions[0])
                                    else:
                                        await show.add_reaction(valid_reactions[0])
                                        await show.add_reaction(valid_reactions[1])
                                    await show.add_reaction(valid_reactions[2])
                                elif str(reaction.emoji) == valid_reactions[1]:
                                    current += 1
                                    await show.delete()
                                    show = await ctx.send(embed = display(current,last_page))
                                    if current == 0:
                                        await show.add_reaction(valid_reactions[1])
                                    elif current == last_page:
                                        await show.add_reaction(valid_reactions[0])
                                    else:
                                        await show.add_reaction(valid_reactions[0])
                                        await show.add_reaction(valid_reactions[1])
                                    await show.add_reaction(valid_reactions[2])

                                elif str(reaction.emoji) == valid_reactions[2]:
                                    
                                    await show.delete()
                                    
                                    embed = discord.Embed(
                                        title = f'> Num page ?',
                                        color = discord.Colour.from_rgb(254, 204, 0),
                                        )
                                    
                                    show2 = await ctx.send(embed = embed)

                                    def check_2(author):
                                        def inner_check(message):
                                            return message.author == author
                                        return inner_check

                                    try:
                                        msg = await self.bot.wait_for('message', check=check_2(ctx.author), timeout=5)
                                        if msg.content in valid_page:
                                            await msg.delete()
                                            await show2.delete()
                                            show2 = await ctx.send(embed = display(int(msg.content),last_page))
                                        else:
                                            embed = discord.Embed(
                                                title = f'> Page {msg.content} non disponible',
                                                color = discord.Colour.from_rgb(254, 204, 0),
                                                )
                                            try:
                                                await msg.delete()
                                                await show2.delete()
                                                show2 = await ctx.send(embed = embed)
                                                # 
                                            except: pass
                                    except asyncio.TimeoutError:
                                        embed = discord.Embed(
                                            title = f'> Annulé [Timeout]',
                                            color = discord.Colour.from_rgb(254, 204, 0),
                                            )
                                        try:
                                            await msg.delete()
                                            await show2.delete()
                                            show2 = await ctx.send(embed = embed)
                                        except: pass
                                    break
                                else:
                                    pass

                        except asyncio.TimeoutError:
                            await show.clear_reaction(valid_reactions[0])
                            await show.clear_reaction(valid_reactions[1])
                            await show.clear_reaction(valid_reactions[2])


                    else:
                        embed = discord.Embed(
                            title = f'~ {arg[0]} ~',
                            color = discord.Colour.from_rgb(254, 204, 0),
                            )
                        for liste in movie_in_list:
                            movie = sq.get_info_with_id(liste[1])
                            movie_name = movie['nom']
                            if liste[4] == 'True':
                                date_vu = datetime.fromtimestamp(liste[3]).strftime('%Y-%m-%d')
                                embed.add_field(name=f':green_square: 〉 {movie_name} | Vu le {date_vu}', value=f'ID: {liste[1]}', inline= False)
                            else:
                                embed.add_field(name=f':red_square: 〉 {movie_name}', value=f'ID: {liste[1]}', inline= False)

                        await ctx.send(embed = embed)
            else:
                await ctx.send(f"> Vous n'avez pas de liste **{arg[0]}**")
        else: 
            await ctx.send("> Erreur dans la commande. [m!help]")

#------------------------------
    @commands.Cog.listener()
    async def on_ready(self):
        print('[+] cogs.classic.list')

# ============================================================================


def setup(bot):
    bot.add_cog(list(bot))        
#FIN ============================================================================
