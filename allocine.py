from bs4 import BeautifulSoup
import requests

style = ["Action","Animation","Arts martiaux","Aventure","Biopic","Bollywood",
            "Comédie","Comédie dramatique","Comédie musicale","Concert","Dessin animé",
            "Divers","Drama","Drame","Epouvante-horreur","Erotique","Espionnage","Evenement Sportif",
            "Expérimental","Famille","Fantastique","Guerre","Historique","Judiciaire","Musical","Médical",
            "Opéra","Policier","Péplum","Romance","Science fiction","Spectacle","Thriller","Western"]

#------------------------------
def get_html_file(url):
    if 'https://www.allocine.fr/film/fichefilm_gen_cfilm=' in url:
        page = requests.get(url)
        content = BeautifulSoup(page.content, "html.parser")
        return content
    else:
        return False

#------------------------------
def check_movie_no_exist(content):
    return content.find(class_='error-page error-404') #True or False 
    
#------------------------------
def get_title(content):
    title= str(content.find(class_="titlebar-title titlebar-title-lg")).split(">")[1][:-5]
    if title:
        return title
    else:
        return 'NA'

def get_ratting(content):
    rat = str(content.findAll(class_="stareval-note")).split(">")
    if rat != ['[]']:
        ratting = rat[1][:-6],rat[3][:-6]
        if ratting[0] == '--':
            ratting = ('NA',ratting[1])
        if ratting[1] == '--':
            ratting = (ratting[0],'NA')
        if ratting[0] == '--' and ratting[1] == '--':
            ratting = ('NA','NA')
    else:
        ratting = ('NA','NA')
    return ratting

#------------------------------
def get_date(div):
    if '<span class="date"' in div[0]:
        return div[0][19:][:-7]
    else:
        return div[0]

#------------------------------
def get_style(div):
    output=[]
    for i in range(2,len(div)):
        check = div[i].split('>')[1].split('<')[0]
        # print(div)
        if check in style:
            output.append(check)
    return output

#------------------------------
def get_time(div):
    return div[1]

#------------------------------
def get_pic(content):
    pic = str(content.find(class_="thumbnail-img")).split('"')[7]
    if pic:
        return pic
    else:
        return 'https://motivatevalmorgan.com/wp-content/uploads/2016/06/default-movie.jpg'

#------------------------------
def get_multi_info(content):
    # info = str(content.find(class_="date")).split("/")
    info = str(content.findAll('div', {"class" : "meta-body-item meta-body-info"})).split("\n")
    output= []
    for ele in info:
        if ('date blue-link">' in ele) or('<strong>' in ele) or ('</strong>' in ele) or ('</div>]' in ele) or ('meta-body-item' in ele) or (ele == '<span class="spacer">/</span>') or (ele == '</span>') or (ele == 'en salle') or (ele == 'en VOD') or (ele == 'en DVD'):
            pass
        else:
            output.append(ele)
    return output

#------------------------------
def get_full_info(url):
    id = url
    url = f'https://www.allocine.fr/film/fichefilm_gen_cfilm={url}.html'
    content = get_html_file(url)
    if content:
        if not check_movie_no_exist(content):
            multi_info = get_multi_info(content)
            movie = {"IDmovie": id,
            "nom": get_title(content),
            "date": get_date(multi_info),
            "duree": get_time(multi_info),
            "ratting": get_ratting(content),
            "img": get_pic(content),
            "style": get_style(multi_info),
            "link": url}
            return movie
        else:
            return False
    else:
        return False