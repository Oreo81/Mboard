from bs4 import BeautifulSoup
import requests

def get_info(url):
    page = requests.get(url)
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
        da = str(soup.find(class_="date")).split(">")[1]
        duree_ = str(soup.findAll('div', {"class" : "meta-body-item meta-body-info"})).split(">")
        sty = str(soup.findAll('div', {"class" : "meta-body-item meta-body-info"})).split(">")

        if titre:
            pass
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

        if pic:
            pass
        else:
            pic = 'https://motivatevalmorgan.com/wp-content/uploads/2016/06/default-movie.jpg'

        if da:
            new = da.replace("\n","")[:-6]
            date = new
        else:
            date = "NA"

        if duree_:
            duree = duree_[7].split("\n")[1]
        else:
            duree = "NA"

        if sty:
            style_check = [x[:-6] for x in sty if x[:-6] in style]
        else:
            style_check = "NA"

        movie = {"nom": str(titre), "date": str(date), "duree": str(duree) ,  "ratting":ratting, "img": str(pic), "style": style_check}
        return movie

# url = 'https://www.allocine.fr/film/fichefilm_gen_cfilm=251390.html'
url = 'https://www.allocine.fr/film/fichefilm_gen_cfilm=25546.html'
print(get_info(url))