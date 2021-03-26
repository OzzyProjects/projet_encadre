# projet_encadre
Projet encadré semestre 1

Web scraper et parser/analyseur synthaxique en chinois, russe, anglais et francais.

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
