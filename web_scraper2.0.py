# -*- coding: utf-8 -*-
#!/usr/bin/env python

""" 
Manuel : ce script se lance avec 2 arguments en ligne de commande
sys.argv[1] : chemin d'acces relatif du dictionnaire de proxies à utiliser
sys.argv[2] : tri selon la fonction des mots
ALL = tous les mots des contextes seront dans le tableau
Sinon, ADJ, VERB, ADV, NOUN pour l'option de tri
Exemple : on cherche à conserver les adjectifs dans le tableau final
python web_scraper2.0.py dico_proxies.txt ADJ
Les fichiers d'urls à recuperer doivent etre placés dans le repertoire ../URLS avec l'extension .txt
sinon, ils seront ignorés
ATTENTION : Ce script necessite l'installation préalable de plusieurs modules via la commande pip (dans le shell):
pip install fake_useragent
pip install bs4
pip install nltk
pip install pymorphy2
pip install razdel
pip install pysbd
pip install spacy
python -m spacy download zh_core_web_sm
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
-> On telecharge le package pour le chinois zh_core_web_sm pour spacy
-> On telecharge le package pour l'anglais en_core_web_sm pour spacy
-> On telecharge le package pour le francais fr_core_news_sm pour spacy
Placer le script dans le dossier PROGRAMMES/
Laisser le programme tourner jusqu'à la fin.
Le tableau récapitulatif se trouvera dans ../TABLEAUX
"""

# modules importés

# modules personnels
import my_parser as mp

import os # module pour utiliser differentes fonctions de l'OS
import bs4 # module BeautifulSoup pour la gestion du contenu html des pages aspirées
from fake_useragent import UserAgent # module pour créer un faux profil
import random # module pour la génération de nombres aléatoires
import re # module pour les expressions regulieres
import requests # module pour le web scraping
import nltk
import sys # module pour avoir accès aux fonctions de l'OS
import time # module pour avoir accès aux objets time
from urllib3.exceptions import InsecureRequestWarning
from html.parser import HTMLParser # module dont on va faire hériter notre classe _HTMLToText

# style CSS du tableau final
CSS_STYLE_FINAL_BOARD = """<script src="../PROGRAMMES/sorttable.js"></script>

<style type="text/css">

#final_table {
    font-size: 12px; color: #333333; width: 70%; border-width: 1px; border-color: #729ea5; border-collapse: collapse; margin: 20px;
    }
    
#langue {
    font-size: 20px; font-weight: 800; font-variant: small-caps;  border-width: 1px; padding: 8px; border-style: solid; border-color: #729ea5; text-align: center;
    background: linear-gradient(0.25turn, #3f87a6, #ebf8e1, #f69d3c); 
    color: black;
    border-bottom: .1em solid #008fb3;
    font-style: oblique 20deg;
    }
    
#menue {
    font-size: 15px; font-weight: 500; font-variant: small-caps;  border-width: 1px; padding: 8px; border-style: solid; border-color: #729ea5; text-align: center;
    background: #ebf8e1; 
    color: black;
    font-weight: bold;
    border-bottom: 2px solid #00b8e6;
    }
    
#final_table tr:nth-child(even) {
    background-color: #c8e0ea;
    }
    
#final_table tr:nth-child(odd) {
    background-color: #fef3e7;
    }
    
#final_table td {
    font-size: 12px; border-width: 1px; padding: 8px; border-style: solid; border-color: #729ea5, text-align: center;
    }
    
#final_table tr:hover {
    background-color: #ffffff; transition: 0.2s all;
    }
    
#final_table > caption {
    text-align: center;
    font-weight: bold;
    color: #4d88ff;
    text-shadow:0 0 2px #ffb31a;
    font-size: 250%;
    border-bottom: .2em solid rgba(53, 124, 124, .5);
    margin-bottom: .3em;
    }
    
table.sortable tbody > th:not(.sorttable_sorted):not(.sorttable_sorted_reverse):not(.sorttable_nosort):after { 
    content: " \25B4\25BE" 
    }
    
</style>
    
<HTML>
<HEAD>
<META CHARSET="UTF-8"/>
<TITLE>Résultats</TITLE>
<LINK rel="stylesheet" type="text/css" href="style3.css">
</HEAD>
<BODY>"""

# HEAD du tableau final
CSS_FINAL_HEAD_BOARD = """<table id="final_table" class="sortable">
<CAPTION>
TABLEAU FINAL
</CAPTION>
<THEAD>
<TR>
<TH id="langue" colspan="3">LAN_GUE</TH>
</TR>
<TR>
<TH id="menue" width="40%">Mot</TH>
<TH id="menue" width="30%">Nature</TH>
<TH id="menue" width="30%">Occurrence</TH>
</TR>
</THEAD>
"""

# style css du tableau d'erreurs
CSS_ERROR_STYLE_BOARD = """<script src=\"../PROGRAMMES/sorttable.js\"></script>

<style type=\"text/css\">

#error_table {
    font-size: 12px; color: #333333; width: 98%; border-width: 1px; border-color: #729ea5; border-collapse: collapse; margin: 20px;
    }
    
#error_table th {
    font-size: 20px; font-weight: 800; font-variant: small-caps; background-color: #acc8cc; border-width: 1px; padding: 8px; border-style: solid; border-color: #729ea5; text-align: center;
    }
    
#error_table tr {
    background-color: #d4e3e5;
    }
    
#error_table tr:nth-child(odd) {
    background-color: #e0ebec;
    }
    
#error_table td {
    font-size: 12px; border-width: 1px; padding: 8px; border-style: solid; border-color: #729ea5, text-align: center;
    }
    
#error_table tr:hover {
    background-color: #ffffff; transition: 0.2s all;
    }
    
#error_table > caption {
    text-align: center;
    font-weight: bold;
    font-size: 200%;
    border-bottom: .2em solid #4ca;
    margin-bottom: .5em;
    }
  
#error_table > thead > tr:first-child > th {
    text-align: center;
    color: black;
    }
  
#error_table td:first-child {
    width: 65%;
    text-align: left;
    }
    
#error_table tr:nth-child(even) {
    background-color: #beccce;
    }
    
#error_table tr:nth-child(odd) {
    background-color: #e0ebec;
    }
  
#error_table td:last-child {
    width: 35%;
    }
  
table.sortable tbody > th:not(.sorttable_sorted):not(.sorttable_sorted_reverse):not(.sorttable_nosort):after { 
    content: " \\25B4\\25BE" 
    }
    
</style>

<HTML>
<HEAD>
<META CHARSET=\"UTF-8\"/>
<TITLE>Fichier d'erreurs</TITLE>
<LINK rel=\"stylesheet\" type=\"text/css\" href=\"style3.css\">
</HEAD>
<BODY>
<table id=\"error_table\" class=\"sortable\">
<CAPTION>
TABLEAU DES ERREURS
</CAPTION>
<THEAD>
<TR>
<TH>Url de la page</TH>
<TH>Type d'erreur </TH>
</TR>
</THEAD>"""

# style css du tableau principal
CSS_STYLE_BOARD = """<script src=\"../PROGRAMMES/sorttable.js\"></script>

<style type=\"text/css\">

#url_table {
    font-size: 12px; color: #333333; width: 98%; border-width: 1px; border-color: #729ea5; border-collapse: collapse; margin: 20px;
    }
    
#url_table th {
    font-size: 20px; font-weight: 800; font-variant: small-caps; background-color: #acc8cc; border-width: 1px; padding: 8px; border-style: solid; border-color: #729ea5; text-align: center;
    }
    
#url_table tr:nth-child(even) {
    background-color: #beccce;
    }
    
#url_table tr:nth-child(odd) {
    background-color: #e0ebec;
    }
    
#url_table td {
    font-size: 12px; border-width: 1px; padding: 8px; border-style: solid; border-color: #729ea5, text-align: center;
    }
    
#url_table tr:hover {
    background-color: #ffffff; transition: 0.2s all;
    }
    
#url_table > caption {
    text-align: center;
    font-weight: bold;
    font-size: 200%;
    border-bottom: .2em solid #4ca;
    margin-bottom: .5em;
    }
  
#url_table > thead > tr:first-child > th {
    text-align: center;
    color: black;
    }
  
#url_table td:first-child {
    width: 5%;
    text-align: center;
    }
    
#url_table td:nth-child(2) {
    width: 5%;
    }
  
#url_table td:nth-child(3) {
    width: 40%;
    }
  
#url_table td:nth-child(4) {
    width: 30%;
    }
  
#url_table td:nth-child(5) {
    width: 10%;
    }
    
#url_table td:nth-child(6) {
    width: 10%;
    }
  
#url_table td:last-child {
    width: 10%;
    }
  
table.sortable tbody > th:not(.sorttable_sorted):not(.sorttable_sorted_reverse):not(.sorttable_nosort):after { 
    content: " \25B4\25BE" 
    }
    
#url_table tfoot {
    border-top: .3em solid #0080ff;
    background-color: #cee;
    }
    
#url_table > tfoot > tr > th {
    font-weight: light;
    text-align:center;
    }
    
#url_table > tfoot > tr > td {
    color : black;
    font-weight: bold;
    text-align:left;
    }
    
#url_table > tfoot > tr:hover {
    background-color: #ccffff; transition: 0.2s all;
    }
    
a.lien_erreur:link { 
    text-decoration:none; 
    }
    
.button {
    font-size: 17px;
    color: black;
    border-radius: 8px;
    transition-duration: 0.4s;
    width : 80%;
    border: 2px solid #80a8ff
    }

.button:hover {
    background-color: #e6eeff; 
    color: blue;
    font-weight: bold;
    }
    
</style>

<HTML>
<HEAD>
<META CHARSET=\"UTF-8\"/>
<TITLE>Mes tableaux d'urls</TITLE>
<LINK rel=\"stylesheet\" type=\"text/css\" href=\"style3.css\">
</HEAD>
<BODY> """

# HEAD du tableau principal
HTML_HEAD_BOARD = """<THEAD>
<TR>
<TH>Numero de la page</TH>
<TH>Encodage original</TH>
<TH>Url de la page </TH>
<TH>Titre de la page</TH>
<TH>Fichier dump</TH>
<TH>Contextes (Nbr)</TH>
<TH>Fichier Index (CSV)</TH>
</TR>
</THEAD>"""

# FOOT du tableau principal (statistiques sur le scraping et boutons pour acceder au fichier d'erreurs)
HTML_FOOT_BOARD = """<TFOOT>
<TR>
<TH>Résultats</TH>
<TD colspan=\"6\">text_to_replace</TD>
</TR>
<TR>
<TH colspan=\"2\" align=\"center\"><button class=\"button\" type=\"button\"><a target=\"_blank\" href=\"tableau_erreurs.html\" class=\"lien_erreur\">Consulter les erreurs ici</a></button></TH>
<TH colspan=\"2\" align=\"center\"><button class=\"button\" type=\"button\"><a target=\"_blank\" href=\"text_to2_replace\" class=\"lien_erreur\">Fichier context</a></button></TH>
<TH colspan=\"3\" align=\"center\"><button class=\"button\" type=\"button\"><a target=\"_blank\" href=\"3text_to3_replace3\" class=\"lien_erreur\">Fichier parsé</a></button></TH>
</TR>
<TR>
<TH colspan=\"3\" align=\"center\"><button class=\"button\" type=\"button\"><a target=\"_blank\" href=\"4text_to4_replace4\" class=\"lien_erreur\">Index DUMP global</a></button></TH>
<TH colspan=\"4\" align=\"center\"><button class=\"button\" type=\"button\"><a target=\"_blank\" href=\"5text_to5_replace5\" class=\"lien_erreur\">Index CONTEXTES global </a></button></TH>
</TR>
</TFOOT>"""



""" VARIABLES GLOBALES """
URLS_PATH = '../URLS'
SCRAPED_PAGES = '../PAGES-ASPIREES'
BOARD_PATH = '../TABLEAUX'
BOARD_HTML = '../TABLEAUX/tableau.html'
ERROR_BOARD_HTML = '../TABLEAUX/tableau_erreurs.html'
FINAL_BOARD_HTML = '../TABLEAUX/tableau_final.html'
DUMP_PATH = '../DUMP-TEXT'
CONTEXT_PATH = '../CONTEXTES'

dict_parsing = {'CHINOIS':'\u514d\u75ab', 'FRANCAIS':'immunité', 'ANGLAIS':'immunity', 'RUSSE':'иммунитет'}
dict_language = {'CHINOIS':'chinese', 'FRANCAIS':'french', 'ANGLAIS':'english', 'RUSSE':'russian'}


# tags autorisés pour le filtrage selon la fonction
filter_tags = ['ALL', 'NOUN', 'VERB', 'ADV', 'ADJ']
        
# On crée notre classe _HTMLToText qui hérite de HTMLParser mais on va modifier quelques attributs et méthodes de la classe mère
# pour supprimer toutes les balises html inutiles, métadonnées et ne récuperer que le texte brut important
class _HTMLToText(HTMLParser):
    
    def __init__(self):
        
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False
        
    def handle_starttag(self, tag, attrs):
        
        if tag in ('p', 'br') and not self.hide_output:
            self._buf.append('\n')
        elif tag in ('script', 'style', 'li', 'fieldset', 'a'):
            self.hide_output = True
            
    def handle_startendtag(self, tag, attrs):
        
        if tag == 'br':
            self._buf.append('\n')
            
    def handle_endtag(self, tag):
        
        if tag == 'p':
            self._buf.append('\n')
        elif tag in ('script', 'style', 'li', 'fieldset', 'a'):
            self.hide_output = False
            
    def handle_data(self, text):
        
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s', ' ', text))
            
    def handle_entityref(self, name):
        
        if name in name2codepoint and not self.hide_output:
            c = chr(name2codepoint[name])
            self._buf.append(c)
            
    def handle_charref(self, name):
        
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(chr(n))
            
    def get_text(self):
        
        return re.sub(r' +', ' ', ''.join(self._buf))

def html_to_text(html_content, language):
    
    """ fonction qui, à partir d'un objet _HTMLToText(), extrait uniquement le texte du contenu html en enlevant
    toutes les infos inutiles, balises, métadonnées, scripts... pour obtenir un texte propre
    html -- objet bs4 dont il faut traiter le contenu html
    renvoie le contenu de bs4 sous une forme textuelle
    """
    
    try:
        # on instancie un parser HTML maison
        parser = _HTMLToText()
        sentences = []
        # on lui donne le contenu html à traiter pour supprimer les balises...
        parser.feed(html_content)
        # on tokenize le texte entier du fichier dump en une liste de phrases grace à NLTK
        if language == 'CHINOIS':
            content = parser.get_text().split('。')
        else:
            content = nltk.sent_tokenize(parser.get_text())
        
        # on parcours chaque phrase du texte
        for sentence in content:
            
            # on supprime les sauts de ligne en trop
            sentence = sentence.replace('\n', '')
            # pareil pour les espaces
            sentence = re.sub(r'\s\s+', ' ', sentence)
            
            # si la phrase fait moins de 30 caracteres ou contient des dates au format JJ:MM ou le symbole '|' etc..., on ne la garde pas
            if len(sentence) > 30 and re.search(r'\d\+:\d+', sentence) is None and sentence.find('|') == -1:
                # sinon on l'ajoute
                if language == 'CHINOIS':
                    sentences.append(sentence + '。\n')
                else:
                    sentences.append(sentence + '\n')
        
        # on renvoie toute la liste concaténée en une seule string
        return sentences
        
    except Exception as error:
        print('html_to_text error {} !!!'.format(error))
        return None

def get_dump_from_html(soup, language, dump_path_file, dump_path_general_file):
    
    """ fonction qui recupere le contenu de l'url en extrayant uniquement les parties de texte pour faciliter la recherche
    par la suite. Elle ecrit le resultat textuel dans un fichier texte et renvoie 1 si aucune erreur n'a été lancée, 0 si une erreur s'est produite
    dump_path_file -- chemin d'acces du fichier dans lequel on va ecrire les données txt issues du code html
    soup -- objet soup du fichier à dumper
    renvoie 1 si aucune erreur ne n'est produite, 0 dans le cas contraire
    """
    
    try:
        # text_content = dump txt extrait du fichier html
        # la méthode prettify() du module bs4 organise le contenu html de l'objet soup de maniere plus claire et hierachisée
        text_content = html_to_text(soup.prettify(), language) 

        if text_content is not None:
            with open(dump_path_file, 'w', encoding='utf-8') as dump_file, open(dump_path_general_file, 'a', encoding='utf-8') as general_file:
                dump_file.writelines(text_content) # ecriture des textes extraits à partir du code hmtl (on enleve les balises, les métadonnées etc...)
                general_file.writelines(text_content) 
            return text_content
        else:
            return 0
            
    except Exception as error: # si une erreur se produit
        print("get_dump_from_html error : {} !!!".format(error))
        return 0
            
def get_contexts_keyword(keyword, dump_text, context_path_file, general_path_file):
    
    contexts = []
    nbr_contextes = 0
    number_line = 0
    before = True
    
    try:
        
        for index in range(len(dump_text) - 1):

            if number_line == index:
                
                if dump_text[index].find(keyword) != -1:
            
                    if before:
                        
                        contexts.append(dump_text[number_line])
                        contexts.append(dump_text[number_line + 1])
                    
                    else:
                        
                        contexts.append(dump_text[number_line - 1])
                        contexts.append(dump_text[number_line])
                        contexts.append(dump_text[number_line + 1])
                        before = True
                    
                    number_line = index + 2
                    nbr_contextes += 1
                else:
                    
                    before = False
                    number_line = index + 1
                    
        result = ''.join(contexts)
        
        with open(context_path_file, 'w', encoding='utf-8') as parsed_file, open(general_path_file, 'a', encoding='utf-8') as general_file:
            parsed_file.write(result + '\n')
            general_file.write(result + '\n')
            
        return nbr_contextes
    
    except Exception as error:
        
        print('get_contexts_keywords error : {}'.format(error))
        return -1
        
    
def get_proxies_list_from_file(proxies_path_file, filter_port = ('80', '8080')):
    
    """ 
    fonction chargée de récuperer en mémoire sous forme d'une liste l'ensemble des adresses IP:port
    qui figure dans le fichier proxies_path_file
    proxies_path_file -- chemin d'accès du fichier dans lequel se trouve la liste des proxies
    filter_port -- tuple qui permet de filtrer uniquemement les proxies avec le/les ports choisis
    par défaut, elle filtre uniquement les proxies HTTP (port 80 et 8080)
    elle renvoie la liste des proxies contenus dans le fichier
    """
    
    if os.path.exists(proxies_path_file): #si le fichier existe, on continue
        proxies_list = []
        with open(proxies_path_file, 'rb') as proxies_file:
            content_file = proxies_file.readlines() 
            for proxy in content_file:
                proxies_list.append(proxy.decode('utf-8').rstrip('\r\n')) #decodage en utf-8 et suppression du retour à la ligne
        if filter_port:
            return list(filter(lambda p : p.endswith(filter_port), proxies_list)) #retourne toutes les ip de proxies avec les ports de filtrage souhaités
        else:
            return proxies_list #si pas de port de filtrage, on retourne tous les proxies
    else:
        print("ERREUR : Le fichier : {} n'existe pas !".format(proxies_path_file))
        return None
        

def get_urls_list(path_urls_file):
    
    """ 
    fonction qui récupere la liste des urls contenues dans path_urls_file
    path_urls_file -- chemin d'accès du fichier dans lequel se trouvent les urls
    elle renvoie les urls récuperées sous forme de liste
    """
    
    if os.path.exists(path_urls_file): # si le fichier existe, on continue
        urls_list = []
        with open(path_urls_file, 'rb') as urls_file:
            content_file = urls_file.readlines()
            for url in content_file:
                urls_list.append(url.decode('utf-8').rstrip('\r\n')) # decodage en utf-8 et suppression du retour à la ligne 
        return list(filter(lambda u: u.startswith('http'), urls_list)) # on récupère tous les éléments commencant par 'http' (des urls)
    else:
        print("ERREUR : Le fichier : {} n'existe pas !".format(path_urls_file))
        return None


def get_files_list(path_folder):
    
    """ 
    fonction qui retourne sous forme de liste tous les fichiers contenues dans le repertoire choisi :
    path_folder -- chemin d'accès du dossier pour lequel il faut récupérer la liste des fichiers sans
    prendre en compte les dossiers et les sous dossiers
    elle renvoie une liste contenant tous les fichiers listés
    """
    
    # verifie dans un premier temps que le répertoire existe
    if os.path.exists(path_folder):
        # si oui, on retourne tous les fichiers txt à l'interieur, pas les dossiers ni les sous-dossiers
        return [f for f in os.listdir(path_folder) if os.path.isfile(os.path.join(path_folder, f)) and f.endswith('.txt')]
    else:
        print("ERREUR : Le repertoire {} n'existe pas !".format(path_folder))
        return None


def is_javascript_content(soup):
    
    """
    fonction qui cherche dans le contenu html de la page si la majorité du code est écrit en javascript
    javascript = contenu dynamique = impossible à scraper de manière traditionnelle
    soup -- objet bs4 qui contient le contenu html de la page à scraper
    renvoie True si il a du code javascript et False sinon 
    """
    
    try:
        
        # cherche toutes les balises <script> avec les valeurs javascript ou text/javascript
        url_scripts = soup.findAll('script', {'language': 'javascript'}, {'type:', 'text/javascript'})
        
        # si la taille de la liste est supérieure à 3 = code javascript trouvé en grande quantité donc on renvoie True
        if len(url_scripts) > 3:
            return True
            
        # sinon, on renvoie False
        return False
        
    # si une exception se déclenche, on renvoie False    
    except Exception as error:
        return False
                

def get_http_url_content(url, http_proxies_list):
    
    """ 
    fonction qui aspire le contenu de la page url sous la forme d'un objet BeautifulSoup
    cette fonction ne fonctionne que pour les urls utilisant le protocole HTTP et HTTPS
    url -- adresse web de la page à aspirer
    http_proxies_list -- liste de proxies http pour éviter le ban
    renvoie le contenu html de la page sous la forme d'un objet BeautifulSoup (code html organisé)
    """

    number_attempts = 0 # nombre d'essais pour récupérer la page
    
    # au bout de 5 essais, on considere que la tentative de scraping a échoué
    while number_attempts != 5:
        
        number_attempts += 1
        
        time.sleep(random.randrange(1,5)) # on fait une pause entre 1 et 5 secondes pour passer le moins possible pour un robot
        fake_user = UserAgent(verify_ssl=False) # creation d'un faux profil aléatoire dans le meme but
        # default no proxy
        proxy = {'no': 'pass'}
        
        if random.randrange(0, 2):
            # une fois sur 2, on tente de récuperer la page via un proxy choisi au hasard dans la liste, sinon pas de proxy
            proxy = {'http': http_proxies_list[random.randrange(0, len(http_proxies_list) - 1)]}
 
        try:
            # on récupere le contenu de la page en question sans prendre en compte l'authentification SSL (verify=False)
            # headers = {'User-Agent':fake_user.random}
            response = requests.get(url, proxies=proxy, headers = {'User-Agent':fake_user.random}, timeout=random.randrange(2, 5), verify=False)
            
            if response.ok: # code HTTP 200 donc la requete est reussie
                # création d'un objet bs4 avec le contenu de la réponse requests.get()
                soup = bs4.BeautifulSoup(response.content, 'lxml')
                
                if not is_javascript_content(soup): 
                    return soup, response # soup = contenu html de la page aspirée
                else:
                    return None, -1 # error javascript ou pb d'encodage
            else:
                # on retourne le code http si il y a une erreur
                return None, response.status_code
        
        except requests.exceptions.ProxyError as proxy_error: # erreur de connexion au proxy
            print("Proxy error on : {} \n code error : {}".format(url, proxy_error))
            continue
        
        except requests.exceptions.ConnectionError as connection_error: # erreur de connexion à la page web
            print("Connection error on : {} \n code error : {}".format(url, connection_error))
            continue
        
        except requests.exceptions.HTTPError as http_error: # erreur HTTP : http code != 200
            print("HTTP error on : {} \n code error : {}".format(url, http_error))
            continue
        
        except requests.exceptions.Timeout as timeout_error: # délai d'attente dépassé
            print("Timeout error on : {} \n code error : {}".format(url, timeout_error))
            continue
        
        except requests.exceptions.RequestException as fatal_error: # tout autre erreur
            print("Fatal error on : {} \n code error : {}".format(url, fatal_error))
            continue
    
    return None, -1
    

def create_html_file(soup, scraped_path):
    
    """ 
    fonction qui crée un fichier html avec le contenu de la page aspirée
    soup -- contenu html de la page aspirée
    url_file -- nom du fichier contenant les urls à la base
    """
    
    try:
        with open(scraped_path, 'w') as html_url_file:
            html_url_file.write(str(soup))
            return 1
    except:
        print("Une erreur s'est produite à l'écriture de : {}".format(scraped_path))
        return 0
        

def main():
    
    # message de bienvenue
    print('\n****************************************************')
    print('*INALCO Webscraper and Data Analyser 2.0           *')
    print('****************************************************\n')
    
    # verifie si le script a bien été lancée avec au moins 1 argument
    # Si non, on informe l'utilisateur et on quitte le script
    if len(sys.argv) < 3:
        print('Il faut au moins deux argments !')
        sys.exit()
        
    # si le second argument ne correspond pas à un tag valide, on en informe l'utilisateur
    # et on quitte le script
    if sys.argv[2] not in filter_tags:
        print('Le tag {} est incorrect pour la recherche !'.format(sys.argv[2]))
        sys.exit()

    # on charge la liste des fichiers d'urls en mémoire
    files_list = get_files_list(URLS_PATH)
    # on charge la liste des proxies en mémoire à partir du fichier de proxies
    proxies_list = get_proxies_list_from_file(sys.argv[1])
    

    # si le chargement du fichier de proxies a échoué, on quitte le script
    if proxies_list is None:
        print('Erreur fatale sur la récupération de la liste de proxies !')
        sys.exit()
    
    # pour supprimer les warnings de urllib3 à cause du bypass SSL
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        
    try:
        
        nltk.data.find('tokenizers/punkt')
        print('La version de nltk est : {}\n.'.format(nltk.__version__))
        
    # si le module NLTK n'est pas installé, on l'installe
    except LookupError:
        
        nltk.download('popular')

    if files_list:
    
        with open(BOARD_HTML, 'w') as html_board, open(ERROR_BOARD_HTML, 'w') as error_board, open(FINAL_BOARD_HTML, 'w') as final_board:
        
            # début écriture des tableaux html
            html_board.write(CSS_STYLE_BOARD + '\n')
            error_board.write(CSS_ERROR_STYLE_BOARD + '\n')
            final_board.write(CSS_STYLE_FINAL_BOARD + '\n')
            file_counter = 1
        
            # on parcours tous les fichiers d'urls dans le dossier ../URLS
            for urls_file in files_list:
            
                # position de l'url dans le fichier
                index = 1
            
                try:
                    # le fichier d'urls doit avoir le format suivant : urls_langue.txt où langue est la langue des urls du fichier
                    language_file = re.search('_(.*?)\.', urls_file).group(1).upper()
                except Exception as Error:
                    language_file = urls_file.rstrip('.txt')
                    continue
                
                print("EXTRACTION DU CONTENU DES URLS {} EN COURS...\n".format(language_file))
            
                url_path_file = os.path.join(URLS_PATH, urls_file)
                urls_list = get_urls_list(url_path_file)
                html_board.write('<table id=\"url_table\" class=\"sortable\">\n')
                html_board.write('<CAPTION>TABLEAU URLS EN ' + language_file + '| MOTIF : ' + dict_parsing[language_file] + '</CAPTION>\n')
                html_board.write(HTML_HEAD_BOARD + '\n')
                final_board.write(CSS_FINAL_HEAD_BOARD.replace('LAN_GUE', language_file) + '\n')
                
                # initialisation des compteurs
                total_url = 0
                total_url_scraped = 0
        
                if urls_list:
            
                    # on parcours toutes les urls du fichier
                    for url in urls_list:
                    
                        file_name = urls_file.rstrip('.txt')
                    
                        # on initialise les principales variables dont nous auront besoin par la suite
                        SCRAPED_PAGES_PATH_FILE = os.path.join(SCRAPED_PAGES, str(index) + file_name) + '.html'
                        DUMP_PATH_FILE = os.path.join(DUMP_PATH, str(index) + file_name) + '.txt'
                        DUMP_INDEX_PATH_FILE = os.path.join(DUMP_PATH, 'index-' + str(index) + file_name) + '.csv'
                        URLS_PATH_FILE = os.path.join(URLS_PATH, file_name) + '.txt'
                        CONTEXT_PATH_FILE = os.path.join(CONTEXT_PATH, str(index) + file_name) + 'parsed.txt'
                        DUMP_PATH_GENERAL_FILE = os.path.join(DUMP_PATH, language_file) + '-dumped.txt'
                        DUMP_INDEX_GENERAL_FILE = os.path.join(DUMP_PATH, language_file) + '-indexed.csv'
                        CONTEXT_INDEX_GENERAL_FILE = os.path.join(CONTEXT_PATH, language_file) + '-indexed.csv'
                        PARSED_PATH_GENERAL_FILE = os.path.join(CONTEXT_PATH, language_file) + '-parsed.txt'
                        CSV_PATH_GENERAL_FILE = PARSED_PATH_GENERAL_FILE.replace('.txt', '.csv')
                        total_url += 1
                
                        # on affiche l'url en cours de scraping
                        print(url)
                    
                        # on récupère le contenu html de la page web et la réponse (ou le code erreur)
                        result, code_error = get_http_url_content(url, proxies_list)
                
                        # si la page est codé uniquement ou presque en javascript, impossible de la récuperer
                        if code_error == -1:
                            print('Javascript Error on {}'.format(url))
                            error_board.write('<tr><td><a target=\"_blank\" href=\"' + str(url) + '\">' + str(url) + '</a></td>')
                            error_board.write('<td>Javascript Error</td></tr>\n')
                    
                        # si la page n'a pas pu etre scrapé, on informe l'utilisateur et on passe à l'url suivante
                        elif result is None :
                            print('Connection Error on : {}'.format(url))
                            error_board.write('<tr><td><a target=\"_blank\" href=\"' + str(url) + '\">' + str(url) + '</a></td>')
                            error_board.write('<td> HTTP code error : ' + str(code_error) + '</td></tr>\n')
                    
                        # tout va bien, on peut poursuivre le traitement des données
                        else:
                        
                            # si la page n'a pas de titre, No title avaliable s'affiche par défaut, sinon on le récupère
                            # de plus, on récupère l'encodage par défaut de la page
                            try:
                                print("Recuperation reussie de la page : {}".format(url))
                                page_title = "No title avaliable"
                                if result.title is not None:    
                                    page_title = result.title.string
                            except AttributeError as error:
                                continue
                        
                            # si l'encodage n'est pas spécifié, on le signale
                            if code_error.encoding is None:
                                code_error.encoding = 'Inconnu'
                                
                            html_board.write('<tr><td>' + str(index) + '</td><td>' + code_error.encoding.upper() + '</td><td><a target=\"_blank\" href=\"' + str(url) + '\">' + str(url) + '</a></td>')
                            html_board.write('<td><a target=\"_blank\" href=\"' + SCRAPED_PAGES_PATH_FILE + '\">' + page_title + '</a></td>')
                            html_path = create_html_file(result, SCRAPED_PAGES_PATH_FILE)
                            dump = get_dump_from_html(result, language_file, DUMP_PATH_FILE, DUMP_PATH_GENERAL_FILE)
                            html_board.write('<td><a target=\"_blank\" href=\"' + DUMP_PATH_FILE + '\">' + "dump file " + str(index) + '</a></td>')
                            nbr_occurrences = get_contexts_keyword(dict_parsing[language_file], dump, CONTEXT_PATH_FILE, PARSED_PATH_GENERAL_FILE)
                            html_board.write('<td><a target=\"_blank\" href=\"' + CONTEXT_PATH_FILE + '\">' + str(nbr_occurrences) + '</a></td>\n')
                            content = mp.load_file(CONTEXT_PATH_FILE)
                            indexes = mp.parse_text(content, dict_parsing[language_file], dict_language[language_file], DUMP_INDEX_PATH_FILE)
                            html_board.write('<td><a target=\"_blank\" href=\"' + DUMP_INDEX_PATH_FILE + '\">' + 'index ' + str(index) + '</a></td></tr>\n')
                            total_url_scraped += 1
                
                        index += 1
                    result_scraping = 'Sur ' + str(total_url) + ' urls au total, ' + str(total_url_scraped) + ' urls ont été scrapées' + ' Réussite = ' + str(round((total_url_scraped / total_url) * 100, 2)) + ' %'
                    
                    # on met à jour le foot du tableau principal avec les chemins des fichiers globaux
                    modified_food_board = HTML_FOOT_BOARD.replace('text_to_replace', result_scraping).replace('text_to2_replace', DUMP_PATH_GENERAL_FILE)
                    modified_food_board = modified_food_board.replace('3text_to3_replace3', PARSED_PATH_GENERAL_FILE)
                    modified_food_board = modified_food_board.replace('4text_to4_replace4', DUMP_INDEX_GENERAL_FILE)
                    html_board.write(modified_food_board.replace('5text_to5_replace5', CONTEXT_INDEX_GENERAL_FILE))
                    html_board.write('</table>\n')
                    
                    # on récupère le contenu du fichier dump global
                    dumped_file = mp.load_file(DUMP_PATH_GENERAL_FILE)
                    # on calcule l'occurrence de tous les mots du fichier dump global et on l'écrit dans un fichier csv
                    result_dumping = mp.word_counter(dumped_file, dict_language[language_file], DUMP_INDEX_GENERAL_FILE)
                    # on récupère le contenu du fichier context global
                    parsed_file = mp.load_file(PARSED_PATH_GENERAL_FILE)
                    # on calcule l'occurrence des mots faisant partie des contextes et on l'écrit dans un fichier csv
                    result_parsing = mp.parse_text(parsed_file, dict_parsing[language_file], dict_language[language_file], CONTEXT_INDEX_GENERAL_FILE)
                    
                    for key, occurrence in result_parsing.items():
            
                        word, nature = key
                        if sys.argv[2] == 'ALL':
                            final_board.write('<tr><td>' +  str(word) + '</td><td>' + nature + '</td><td>' + str(occurrence) + '</td></tr>\n')
                        else:
                            if nature.find(sys.argv[2]) != -1:
                                final_board.write('<tr><td>' +  str(word) + '</td><td>' + nature + '</td><td>' + str(occurrence) + '</td></tr>\n')
                    
                    final_board.write('</table>\n')
                    file_counter += 1
                    
                else:
                    print("ERREUR sur la recuperation des urls !")
                
            # on ferme les differents tableaux html
            error_board.write('</table>\n')
            error_board.write('</body></html>\n')
            html_board.write('</body></html>\n')
            final_board.write('</body></html>\n')
    else:
        print("ERREUR sur la recuperation de la liste des fichiers url du dossier")

        
#si notre module est exécuté en tant que script, on execute la fonction main() mais pas si on 
#l'importe uniquement en tant que module dans un autre script
if __name__ == "__main__":
    
    main()
    





        
    
    







            
    
