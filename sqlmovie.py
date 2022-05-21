import sqlite3 
from ast import literal_eval

sqlconnect = sqlite3.connect('./media/db/mlist.db')
cursorsql = sqlconnect.cursor()

def cursor():
    return cursorsql

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
    movie = movie.fetchall() 
    if len(movie) == 0:
        return False
    else:
        output = {
        "IDmovie": movie[0][0],
        "nom": movie[0][1],
        "date": movie[0][2],
        "duree": movie[0][3] ,
        "ratting":literal_eval(movie[0][4]),
        "img": movie[0][5],
        "style": literal_eval(movie[0][6]),
        "link": movie[0][7]}
        return output

def commit():
    sqlconnect.commit()