# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""***************MODULE POUR LE PARSING********************"""

import codecs
from collections import defaultdict # pour l'instanciation d'un dictionnaire avec un type particulier en valeur
import operator # module pour effectuer des operations sur des structures complexes (dict, list...)
import csv # module pour l'utilisation des fichiers csv
import re # module pour les expressions regulieres

# modules pour le parsing et l'analyse linguistique en russe
import pymorphy2
from razdel import sentenize as sentenize_russian
from razdel import tokenize as tokenize_russian

# modules pour le parsing et l'analyse linguistique en francais et en anglais
import nltk 
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

# modules pour le parsing et l'analyse linguistique en francais, anglais et chinois
import spacy
from pysbd.utils import PySBDFactory


def load_file(path_file):
    
    """
    fonction qui charge le contenu d'un fichier en mémoire
    path_file -- fichier à charger en mémoire
    renvoie le contenu du fichier chargé en mémoire
    """
    
    try:
        
        with open(path_file, 'rb') as file_:
            return file_.read().decode('utf-8')
    
    except Exception as error:
        
        print('load_file error : {} !!!'.format(error))
        return None


def parse_text(content, keyword, language, csv_filename):
    
    if language == 'english':
        return parse_english_text(content, keyword, csv_filename)
    elif language == 'french':
        return parse_french_text(content, keyword, csv_filename)
    elif language == 'russian':
        return parse_russian_text(content, keyword, csv_filename)
    else:
        return parse_chinese_text(content, keyword, csv_filename)
            

def extract_context(keyword, sentence):
    
    """
    fonction qui recupere le contexte pertinent autour du keyword en fonction de sa position et/ou fonction dans la phrase
    keyword -- mot clé autour duquel rechercher le contexte
    sentence -- string, phrase dans laquelle chercher le contexte
    renvoie le contexte sous forme d'une liste de mots
    """
    
    context = list()
    
    # si le mot-clé est sujet ou qu'il se trouve en début de phrase, le contexte pertinant est à droite
    if keyword.dep_.find('nsubj') != -1 or keyword.dep_.find('ROOT') != -1 or keyword.i < 3:
        
        # on charge le contexte à partir de la position du keyword (keyword.i = position du keyword)
        context = list(sentence[keyword.i:])
        
        # on ajoute tous les mots qui suivent tant qu'on ne trouve pas un signe particulier de ponctuation, un nouveau sujet
        # ou tant qu'on n'est pas arrivé à la fin de la phrase
        for i, word in enumerate(context):
            if any(x in word.text for x in [';', ':', '.', '-', '...', '!', '?']) or word.dep_.find('nsubj') != -1:
                context = context[:i]
                break
    else:
        
        # sinon, le mot est à un cas oblique = complement donc il est en fin de phrase ou de proposition (en général)
        # le contexte est generalement avant (donc à gauche)
        context = list(sentence[:keyword.i - 1])
        context.sort(key=lambda x:x.i, reverse=True)
        list_context = list()
        
        # on parcourt la phrase en sens inverse jusqu'au début de la phrase, un signe de ponctuation ou un autre nom
        # qui occupe la fonction de sujet dans la phrase
        for word in context:
            
            if not any(x in word.text for x in [';', ':', '.', ',']) or word.dep_.find('nsubj') == -1:
                list_context.append(word)
            else:
                break
        
        # on renverse la liste pour retrouver l'ordre des mots initial
        list_context.reverse()
        # on ajoute le keyword
        list_context.append(keyword)
        context = list_context
        
    # si le contexte fait moins de 3 tokens, on ne le garde pas = aucun portée sémantique
    if len(context) < 3:
        return None
    else:
        return context
    
def parse_french_text(french_content, keyword, csv_filename):
    
    """
    fonction chargée de parser du contenu texte en francais en récuperant le contexte pertinant
    autour du keyword en fonction de la fonction de ce dernier dans la phrase.
    Si le keyword est sujet, alors le contexte interessant est à droite dans la phrase.
    Si il n'est pas sujet ou racine, le contexte interessant est à gauche. 
    Puis elle effectue un comptage des occurrences des mots du contexte sous leur forme de lemme pour chaque
    phrase, puis elle enregistre les résultats dans un fichier csv
    french_content -- contenu texte en francais
    keyword -- mot clé
    csv_filename -- path du fichier csv dans lequel enregistrer les résultats
    """
    
    # on charge les stop words du francais en mémoire
    stop_words = list(stopwords.words('french'))
    # on charge spacy avec le package francais
    nlp = spacy.load('fr_core_news_sm')
    # on instancie notre dictionnaire qui servira à compter les occurrences
    result_parsing = defaultdict(int)
    
    # on sentenize le texte francais
    french_content = nltk.sent_tokenize(french_content, language = 'french')
    
    # pour chaque phrase du texte
    for sentence in french_content:
         
        # si la phrase contient l'occurrence du keyword
        if sentence.find(keyword) != -1:
             
            # on tokenize la phrase en mots
            doc = nlp(sentence)
            # on etablit la liste des positions des occurrences du keyword dans la phrase
            keyword_ = list(filter(lambda i : i.text == keyword, doc))
            if len(keyword_) > 0:
                # on récupère le contexte du mot en fonction de sa fonction dans la phrase
                contexte = extract_context(keyword_[0], doc)
                if contexte is not None:
                    # on compte le nombre d'occurrences pour chaque mot du contexte
                    for word in contexte:
                        # si le mot n'est pas dans les stop words ou qu'il ne s'agit pas d'un signe de ponctuation, 
                        # ou si ce n'est pas un nombre, on compte son occurrence 
                        if word.lemma_ not in stop_words and word.pos_.find('PUNCT') == -1 and word.pos_.find('NUM') == -1:
                            if (word.lemma_, word.pos_) not in result_parsing.keys():
                                result_parsing[(word.lemma_, word.pos_)] = 1
                            else:
                                result_parsing[(word.lemma_, word.pos_)] = result_parsing.get((word.lemma_, word.pos_), 0) + 1
    
    # on classe les entrées du dictionnaires en fonction de l'occurrence de chaque mot
    # de la plus élevée à la plus petite
    list_parsing = dict(sorted(result_parsing.items(), key=lambda x: x[1], reverse=True))
    
    # on écrit un fichier csv index par fichier
    with open(csv_filename, 'w') as index_file:
        
        fieldnames = ['mot', 'occurrence', 'nature']
        csv_writer = csv.DictWriter(index_file, fieldnames=fieldnames, delimiter='\t')
        csv_writer.writeheader()
        
        for key, occurrence in list_parsing.items():
            word, nature = key
            csv_writer.writerow({'mot':word, 'occurrence':occurrence, 'nature':nature})
    
    return list_parsing
    

def parse_english_text(english_content, keyword, csv_filename):
    
    """
    fonction chargée de parser du contenu texte en anglais en récuperant le contexte pertinant
    autour du keyword en fonction de la fonction de ce dernier dans la phrase.
    Si le keyword est sujet, alors le contexte interessant est à droite dans la phrase.
    Si il n'est pas sujet ou racine, le contexte interessant est à gauche. 
    Puis elle effectue un comptage des occurrences des mots sous leur forme de lemme du contexte pour chaque
    phrase, puis elle enregistre les résultats dans un fichier csv
    english_content -- contenu texte en anglais
    keyword -- mot clé
    csv_filename -- path du fichier csv dans lequel enregistrer les résultats
    """
    
    # on ajoute d'autres mots ininteressants pour la recherche
    stop_words = list(stopwords.words('english'))
    # on charge spacy avec le package anglais
    nlp = spacy.load('en_core_web_sm')
    result_parsing = defaultdict(int)
    
    # on sentenize le texte englais
    english_content = nltk.sent_tokenize(english_content, language = 'english')
    
    # on parcours chaque phrase du texte
    for sentence in english_content:
         
        # si le keyword se trouve dans la phrase
        if sentence.find(keyword) != -1:
             
            # on tokenize la phrase en mots
            doc = nlp(sentence)
            # on etablit la liste des positions des occurrences du keyword dans la phrase
            keyword_ = list(filter(lambda i : i.text == keyword, doc))
            if len(keyword_) > 0:
                # on récupère le contexte du mot en fonction de sa fonction dans la phrase
                contexte = extract_context(keyword_[0], doc)
                if contexte is not None:
                    # on compte le nombre d'occurrences pour chaque mot du contexte
                    for word in contexte:
                        # si le mot n'est pas dans les stop words ou qu'il ne s'agit pas d'un signe de ponctuation, 
                        # ou si ce n'est pas un nombre, on compte son occurrence 
                        if word.lemma_ not in stop_words and word.pos_.find('PUNCT') == -1 and word.pos_.find('NUM') == -1:
                            if (word.lemma_, word.pos_) not in result_parsing.keys():
                                result_parsing[(word.lemma_, word.pos_)] = 1
                            else:
                                result_parsing[(word.lemma_, word.pos_)] = result_parsing.get((word.lemma_, word.pos_), 0) + 1
    
    # on classe les entrées du dictionnaires en fonction de l'occurrence de chaque mot
    # de la plus élevée à la plus petite
    list_parsing = dict(sorted(result_parsing.items(), key=lambda x: x[1], reverse=True))
    
    # on écrit un fichier csv index par fichier
    with open(csv_filename, 'w') as index_file:
        
        fieldnames = ['mot', 'occurrence', 'nature']
        csv_writer = csv.DictWriter(index_file, fieldnames=fieldnames, delimiter='\t')
        csv_writer.writeheader()
        
        for key, occurrence in list_parsing.items():
            word, nature = key
            csv_writer.writerow({'mot':word, 'occurrence':occurrence, 'nature':nature})
    
    return list_parsing
    
    
# PAS ENCORE AU POINT PAR RAPPORT AUX AUTRES LANGUES
def parse_chinese_text(chinese_content, keyword, csv_filename):
    
    """
    fonction chargée de parser du contenu texte en chinois en récuperant le contexte pertinant
    autour du keyword, puis en effectuant un comptage des occurrences des mots ayant été lémmatisés du contexte pour chaque
    phrase, puis elle enregistre les résultats dans un fichier csv
    chinese_content -- contenu texte en chinois
    keyword -- mot clé
    csv_filename -- path du fichier csv dans lequel enregistrer les résultats
    """

    # on charge spacy avec le package chinois
    nlp = spacy.load('zh_core_web_sm')
    # on lui ajoute un pipeline pour sentenizer le texte chinois
    nlp.add_pipe(PySBDFactory(nlp), first=True)
    # on initialise la liste des mots ininteressants pour la recherche contextuelle, aussi appelés des stop words
    stop_words = codecs.open('chinese_stopwords.txt', 'r', encoding='utf-8').read().split('\r\n')
    # on sentenize le texte chinois
    chinese_content = nlp(chinese_content)
    result_parsing = defaultdict(int)
    
    #on parcours chaque phrase du texte
    for sentence in chinese_content.sents:
        
        if re.search(u'\u514d\u75ab', sentence.text, re.U):
        
            # on désactive le module de sentenizing
            with nlp.disable_pipes('PySBDFactory'):
            
                # on découpe chaque phrase en une liste de tokens
                chinese_words = nlp(sentence.text)
                # keyword_ = list(filter(lambda i : i.text == u'\u514d\u75ab', chinese_words))
                # on récupère le contexte du mot en fonction de sa fonction dans la phrase
                contexte = chinese_words
                if contexte is not None:
                    # on compte le nombre d'occurrences pour chaque mot du contexte
                    for word in contexte:
                        # si le mot n'est pas dans les stop words ou qu'il ne s'agit pas d'un signe de ponctuation, 
                        # ou si ce n'est pas un nombre, on compte son occurrence 
                        if word.lemma_ not in stop_words and word.pos_.find('PUNCT') == -1 and word.pos_.find('NUM') == -1:
                            if (word.lemma_, word.pos_) not in result_parsing.keys():
                                result_parsing[(word.lemma_, word.pos_)] = 1
                            else:
                                result_parsing[(word.lemma_, word.pos_)] = result_parsing.get((word.lemma_, word.pos_), 0) + 1
    
    # on classe les entrées du dictionnaires en fonction de l'occurrence de chaque mot
    # de la plus élevée à la plus petite
    list_parsing = dict(sorted(result_parsing.items(), key=lambda x: x[1], reverse=True))
    
    # on écrit un fichier csv index par fichier
    with open(csv_filename, 'w') as index_file:
        
        fieldnames = ['mot', 'occurrence', 'nature']
        csv_writer = csv.DictWriter(index_file, fieldnames=fieldnames, delimiter='\t')
        csv_writer.writeheader()
        
        for key, occurrence in list_parsing.items():
            word, nature = key
            csv_writer.writerow({'mot':word, 'occurrence':occurrence, 'nature':nature})
    
    return list_parsing
    
def extract_russian_context(keyword, keyword_offset, tag_keyword, tags):
    
    """
    fonction qui recupere le contexte pertinent autour du keyword en fonction de sa position et/ou fonction dans la phrase
    keyword -- mot clé autour duquel rechercher le contexte
    keyword_offset -- position du keyword dans la phrase
    tag_keyword -- tag pour le keyword
    tags -- liste des tags des mots
    renvoie le contexte autour du mot clé
    """
    
    context = list()
    
    # si le mot-clé est au nominatif ou qu'il se trouve en début de phrase, le contexte interéssant est à droite
    if {'NOUN', 'nomn'} in tag_keyword or keyword_offset < 3:
        
        context = tags[keyword_offset:]
        
        # on ajoute tous les mots tant qu'on ne trouve pas un signe de ponctuation, un nom au nominatif
        # ou qu'on n'est pas arrivé à la fin de la phrase
        for i, infos in enumerate(context):
            if any(x in infos.normal_form for x in [';', '.']) or {'NOUN', 'nomn'} in infos.tag:
                context = context[:i]
                break
    else:
        
        # sinon, le mot est à un cas oblique = complement donc il est en fin de phrase ou de proposition (en général)
        # donc le contexte interessant est avant (à gauche)
        context = tags[:keyword_offset]
        context.sort(key=lambda x:x[0], reverse=True)
        list_context = list()
        
        # on parcourt la phrase en sens inverse jusqu'au début de la phrase ou à un signe de ponctuation ou tant que l'on ne
        # rencontre pas un nom au nominatif (subordonée...)
        for infos in context:
            
            if not any(x in infos.normal_form for x in [';', ':', '.', ',', '...', '-']) and (infos.normal_form != keyword and {'NOUN', 'nomn'} not in infos.tag):
                list_context.append(infos)
            else:
                break
        
        # on renverse la liste pour retrouver l'ordre des mots initial
        list_context.reverse()
        # on ajoute le keyword
        context = list_context
    
    # si le contexte fait moins de 4 tokens, on ne le garde pas = aucun portée sémantique
    if len(context) < 4:
        return None
    else:
        return context
        
    
def parse_russian_text(russian_content, keyword, csv_filename):

    # on initialise le parser russe pymorphy2.MorphAnalyzer()
    morph = pymorphy2.MorphAnalyzer()
    # on ajoute d'autres stop words inutiles en russe pour l'analyse linguistique
    stop_words = list(stopwords.words('russian'))
    # on tokenize le texte russe en phrases
    russian_content = list(sentenize_russian(russian_content))
    result_parsing = defaultdict(int)
    
    # on parcours l'ensemble du texte tokénisé sous la forme de phrases
    for sentence in russian_content:
        
        # si la phrase comporte le keyword
        if sentence.text.find(keyword) != -1:
            
            # on tokenize la phrase en mots = tokens
            sequence_words = tokenize_russian(sentence.text)
            # on recupere les tags de tous les tokens
            tags = [morph.parse(t.text)[0] for t in sequence_words]
            # on associe chaque mot (tag.normal_form) à son offset (position dans la phrase)
            tags_offsets = list(zip(list(range(len(tags))), tags))
            # on recupere les offsets du keyword, si le keyword est présent à plusieurs reprises
            keyword_offsets_tags = list(map(lambda x : (x[0], x[1]), filter(lambda y: y[1].normal_form == keyword, tags_offsets)))
            keyword_offsets = list(map(lambda x: x[0], keyword_offsets_tags))
            keyword_tag = list(map(lambda x: x[1].tag, keyword_offsets_tags))
                
            if len(keyword_offsets) == 1:
                
                # on recupere le contexte russe
                russian_context = extract_russian_context(keyword, keyword_offsets[0], keyword_tag[0], tags)
                
                # si le contexte russe est pertinent
                if russian_context is not None:
                    
                    # on compte le nombre d'occurrences pour chaque mot du contexte
                    for word in russian_context:
                        # si le mot n'est pas dans les stop words, on compte son occurrence
                        if word.normal_form not in stop_words and len(word.normal_form) > 1:
                            nature = str(word.tag).split(',')[0][:4]
                            if (word.normal_form, nature) not in result_parsing.keys():
                                result_parsing[(word.normal_form, nature)] = 1
                            else:
                                result_parsing[(word.normal_form, nature)] = result_parsing.get((word.normal_form, nature), 0) + 1
    
    # on récupere les mots les plus communs en dehors des stop words
    list_parsing = dict(sorted(result_parsing.items(), key=lambda x: x[1], reverse=True))
    
    # on écrit un fichier csv index par fichier
    with open(csv_filename, 'w') as index_file:
        
        fieldnames = ['mot', 'occurrence', 'nature']
        csv_writer = csv.DictWriter(index_file, fieldnames=fieldnames, delimiter='\t')
        csv_writer.writeheader()
        
        for key, occurrence in list_parsing.items():
            word, nature = key
            csv_writer.writerow({'mot':word, 'occurrence':occurrence, 'nature':nature})
    
    return list_parsing
                
    
def word_counter(content, language, csv_filename):
    
    """
    fonction qui compte les occurrences de chaque mot et ecrit le résultat dans un fichier csv
    Les mots sont classés selon leur occurrence, de la plus grande à la plus petite
    content -- string contenant le texte brut à traiter
    language -- langue dans laquel il faut compter l'occurrence des mots
    csv_filename -- nom du fichier csv dans lequel il faut écrire le résultat
    """
    
    # si c'est du chinois, on utilise spacy pour tokeniser le contenu
    if language == 'chinese':
        
        # on charge spacy avec le package chinois
        nlp = spacy.load('zh_core_web_sm')
        # on tokenize le texte en mots
        words = nlp(content)
        
    # sinon, on utilise RegexpTokenizer('\w+')
    else:
        
        # on initialise notre tokenizer de mots
        tokenizer = RegexpTokenizer('\w+')
        # on tokenize le texte en mots
        words = tokenizer.tokenize(content)
        
    # on instancie le dictionnaire stats qui va servir à compter les occurrences
    stats = defaultdict(int)
    
    # pour chaque mot du texte
    for word in words:
        # on le met en miniscule pour ne pas prendre en compte la casse
        word = str(word).lower()
        # si le mot est nouveau, on crée une entrée dans le dictionnaire stats
        if word not in stats.keys():
            stats[word] = 1
        # sinon, on incrémente son occurrence
        else:
            stats[word] = stats.get(word, 0) + 1
            
    # on trie les clés du dictionnaire selon leur occurrence
    sorted_stats = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
            
    #on écrit les résultats dans le fichier csv
    with open(csv_filename, 'w') as csv_file:
        
        fieldnames = ['mot', 'occurrence']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')
        csv_writer.writeheader()
        
        for word, occurrence in sorted_stats.items():
            csv_writer.writerow({'mot':word, 'occurrence':occurrence})
