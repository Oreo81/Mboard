from datetime import *
from time import *
import discord
from discord.ext import commands
import sqlite3 
import asyncio #for timeout error
from bs4 import BeautifulSoup
import requests
from ast import literal_eval

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

def check_movie_in_list(IDmovie,idadmin):
    check = cursorsql.execute(f"SELECT IDlist FROM inlist where IDmovie='{IDmovie}' and IDadmin ='{idadmin}'")
    check = check.fetchall()
    if len(check) == 0:
        return True
    else:
        return False
        
def get_id_list(name_list,idadmin):
    check = cursorsql.execute(f"SELECT IDlist FROM list WHERE IDadmin = {idadmin} AND name='{name_list}'")
    check = check.fetchall()
    return check[0][0]

def get_info_with_id(IDmovie):
    movie = cursorsql.execute(f"SELECT * FROM movie where IDmovie={IDmovie}")
    movie = movie.fetchall()[0] 
    output = {
    "IDmovie": movie[0],
    "nom": movie[1],
    "date": movie[2],
    "duree": movie[3] ,
    "ratting":literal_eval(movie[4]),
    "img": movie[5],
    "style": literal_eval(movie[6]),
    "link": movie[7]}
    return output

def displaymod(movie):
    genre = ""
    for k in movie['style']:
        genre += k +" / "
    genre = genre[:-2]

    ratting = ""
    for k in movie['ratting']:
        ratting += k+" / "
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

def get_info(url):
    url_page = f'https://www.allocine.fr/film/fichefilm_gen_cfilm={url}.html'
    page = requests.get(url_page)
    soup = BeautifulSoup(page.content, "html.parser")
    not_found = soup.find(class_='error-page error-404')
    style = ["Action","Animation","Arts martiaux","Aventure","Biopic","Bollywood",
            "Comédie","Comédie dramatique","Comédie musicale","Concert","Dessin animé",
            "Divers","Drama","Drame","Epouvante-horreur","Erotique","Espionnage","Evenement Sportif",
            "Expérimental","Famille","Fantastique","Guerre","Historique","Judiciaire","Musical","Médical",
            "Opéra","Policier","Péplum","Romance","Science fiction","Spectacle","Thriller","Western"]

    if not_found:
        return False
    else:
        titre = str(soup.find(class_="titlebar-title titlebar-title-lg")).split(">")[1][:-5]
        rat = str(soup.findAll(class_="stareval-note")).split(">")
        pic = str(soup.find(class_="thumbnail-img")).split('"')[7]
        try:
            da = str(soup.find(class_="date")).split(">")[1]
            if da:
                new = da.replace("\n","")[:-6]
                date = new
            else: date = "NA"
        except:
            date = "NA"
        duree_ = str(soup.findAll('div', {"class" : "meta-body-item meta-body-info"})).split(">")
        sty = str(soup.findAll('div', {"class" : "meta-body-item meta-body-info"})).split(">")

        if titre: pass
        else: titre = 'NA'

        if rat:
            ratting = rat[1][:-6],rat[3][:-6]
            if ratting[0] == '--':
                ratting = ('NA',ratting[1])
            if ratting[1] == '--':
                ratting = (ratting[0],'NA')
            if ratting[0] == '--' and ratting[1] == '--':
                ratting = "NA"
        else:
            ratting = "NA"

        if pic: pass
        else: pic = 'https://motivatevalmorgan.com/wp-content/uploads/2016/06/default-movie.jpg'

        if duree_: duree = duree_[7].split("\n")[1]
        else: duree = "NA"

        if sty: style_check = [x[:-6] for x in sty if x[:-6] in style]
        else: style_check = "NA"

        movie = {"IDmovie": url,"nom": str(titre), "date": str(date), "duree": str(duree) ,  "ratting":ratting, "img": str(pic), "style": style_check, "link": str(url_page)}
        print(movie)
        return movie

class list(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="listdel",aliases=['ld', 'listd', 'dell'])
    async def listdel(self,ctx,*name):
        id_admin = ctx.author.id
        if not name:
            await ctx.send("> Mettre un nom de liste [m!help]")
        else:
            name = str(name[0])
            if not name_alrdy_take(name,id_admin):
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
                        id_list = get_id_list(f'{name}',id_admin)
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
        sqlconnect.commit()

    @commands.command(name="listcreate",aliases=['lc', 'listc', 'createl'])
    async def listcreate(self,ctx,*name):
        id_admin = ctx.author.id
        if not name:
            await ctx.send("faut mettre un nom")
        else:
            name = str(name[0])
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

    @commands.command(name="listaddmovie",aliases=['lam', 'laddmovie'])
    async def listadd(self,ctx, *arg):
        idadmin = ctx.author.id
        if len(arg) != 2:
            # await ctx.send("> Pour rajouté un film, il faut l'id du film", file=discord.File('media/img/exemple.png'))
            await ctx.send("> Erreur dans la commande. [m!help]")
        else:
            name_list= arg[1]
            url = arg[0]
            movie_link = get_info(url)
            list_exist = name_alrdy_take(name_list,idadmin)
            if list_exist:
                if not movie_link:
                    await ctx.send("> Ce film n'existe pas")
                else:
                    if check_movie_in_list(url,idadmin):
                        movie_existe = cursorsql.execute(f"SELECT IDmovie FROM movie WHERE IDmovie = {url}")
                        movie_existe = movie_existe.fetchall()
                        IDlist = get_id_list(name_list,idadmin)
                        print(IDlist)
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
            sqlconnect.commit()

    @commands.command(name="remove",aliases=['rm', 'r'])
    async def remove(self,ctx, *arg):
        idadmin = ctx.author.id
        if len(arg) != 2:
            await ctx.send("> Erreur dans la commande. [m!help]")
        else:
            IDmovie = arg[0]
            nom_list = arg[1]
            id_list = get_id_list(nom_list,idadmin)
            cursorsql.execute("DELETE FROM inlist WHERE IDlist = (?) and IDmovie = (?)",(id_list,IDmovie))
            await ctx.send(f"> Le film à été enlever de la liste")
            sqlconnect.commit()

    @commands.command(name="film",aliases=['f', 'movie'])
    async def film(self,ctx, *arg):
        idadmin = ctx.author.id
        IDmovie = arg[0]
        if len(arg) != 1:
            await ctx.send("> Erreur dans la commande. [m!help]")
        else:
            movie = get_info_with_id(IDmovie)
            embed = displaymod(movie)
            await ctx.send(f"> Information: {movie['nom']}", embed = embed)
           
    @commands.command(name="listsee",aliases=['l', 'ls'])
    async def listsee(self,ctx, *arg):
        idadmin = ctx.author.id
        if len(arg) == 0:
            user_list = cursorsql.execute(f"SELECT * FROM list WHERE IDadmin = {idadmin}")
            user_list = user_list.fetchall()
            print(user_list)


        elif len(arg) == 1:
            if name_alrdy_take(arg[0],idadmin):
                id_list = get_id_list(arg[0],idadmin)
                movie_in_list = cursorsql.execute(f"SELECT * FROM inlist WHERE IDadmin = {idadmin} and IDlist = {id_list}")
                movie_in_list = movie_in_list.fetchall()
                await ctx.send(f"{movie_in_list}")
            else:
                await ctx.send(f"> Vous n'avez pas de liste **{arg[0]}**")
        else: 
            await ctx.send("> Erreur dans la commande. [m!help]")

    @commands.Cog.listener()
    async def on_ready(self):
        print('[+] cogs.classic.list')

# ============================================================================


def setup(bot):
    bot.add_cog(list(bot))        
#FIN ============================================================================
