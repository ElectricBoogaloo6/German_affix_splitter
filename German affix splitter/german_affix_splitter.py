### imports 
import pandas as pd
import numpy as np
import chardet
import difflib
import pprint as pp
import pickle
import contextlib
import io
from nltk.stem import SnowballStemmer
from nltk.stem.cistem import Cistem
from german_compound_splitter import comp_split
from wordfreq import word_frequency
from wordfreq import zipf_frequency


def get_file(filepath, compound_filepath):
    """
    Load the data from .txt file with correct encoding for further breakdown. 
    Additionally, provide a file path to the large list of German words for the compound breaker to work.
    Returns data as a list.
    
    filepath = a text file containing a word per line OR a SUBTLEX text file.
    compound_filepath = text file consisting of large collection of german words, for use in compound splitting.
    """
    # saved filepath for compound splitter
    get_file.compound_splitter_filepath = compound_filepath
    
    with open(compound_filepath, 'rb') as large_list:
        large_list_data = large_list.read()

    col_name = ['basic_words']
    german_basic_word_file = pd.read_csv(compound_filepath, sep="\t", names=col_name, header=None, encoding = 'utf-8')
    german_basic_word_file = german_basic_word_file['basic_words'].str.lower()
    german_basic_word_list = german_basic_word_file.tolist()
    
    get_file.german_basic_word_list = german_basic_word_list
    
    # Getting the encoding string
    with open(filepath, 'rb') as file:
        encode = str(list(chardet.detect(file.read()).values())[0])
    
    print(f'Getting data from file: {filepath}')
    print('\n')
    
    ### if the text file is from subtlex: isolate the words with correct spelling and add them.
    if filepath.find('SUBTLEX') != -1:
        subtlex_data = pd.read_csv(filepath, sep="\t", header=None, encoding = encode)
        subtlex_data = subtlex_data.rename(columns=subtlex_data.iloc[0]).drop(subtlex_data.index[0]).reset_index(drop=True) # Sets the correct headers
        
        # Change frequency column to integer
        subtlex_data["WFfreqcount"] = subtlex_data["WFfreqcount"].astype('int')
        
        # Get only correctly spelled words
        subtlex_data = subtlex_data.loc[subtlex_data["spell-check OK (1/0)"] == 1]
        
        # Isolating the word column and turning all words lowercase
        subtlex_data_for_copy = subtlex_data['Word']
        subtlex_data_copy = subtlex_data_for_copy.copy()
        subtlex_data_copy.columns = ['Words']
        data = [w for w in subtlex_data_copy]
        
        with open('text_file_for_compound_split.txt', 'w') as for_split:
            for line in data:
                for_split.write("%s\n" % line)
        
        return data
    
    else:
        with open(filepath, 'r', encoding=encode) as f:
            data = f.read().splitlines()
        return data
    
def sb_stemming(data):
    """
    Function for snowball stemming the provided words from data.
    Returns a list of stemmed words
    
    data: list of words to be stemmed.
    """
    # Initialise
    sb_stemmer = SnowballStemmer("german", ignore_stopwords=True)
    sb_stemmed_words = []
    
    # Snowball stemming the words 
    for word in data:
        sb_stemmed = sb_stemmer.stem(word)
        sb_stemmed_words.append(sb_stemmed)
        
    return sb_stemmed_words

def cistem_stemmeing(data):
    """
    Function for cistem stemming the provided words from data.
    Returns a list of stemmed words
    
    data: list of words to be stemmed.
    """
    
    # Cistem stemming the words
    cistem_stemmed_words = []
    
    for word in data:
        cistem_stemmer = Cistem().segment(word)
        cistem_stemmed_words.append(list(cistem_stemmer))
        
    return cistem_stemmed_words

def stem_differences(data, sb_stemmed_words):
    """
    Function for getting the differences between stems and non- stems, manually getting suffixes from the differences.
    Returns list of the differences (suffixes)
    
    data = original list of non stemmed words
    sb_stemmed_words = snowball stemmed words
    """
    # Converting to tuples for comparison and making data lowercase
    data = [w.lower() for w in data]
    combo = list(zip(data, sb_stemmed_words)) 
    
    dif_suffixes = []
    
    for idx, i in enumerate(data):
        potential_suffix = []
        ### Getting differences using the difflib module
        for i,s in enumerate(difflib.ndiff(i,sb_stemmed_words[idx])):
            
            ### if the character is not different = continue
            if s[0]==' ': continue
                
            ### if chacater has minus before it (could be part of suffix)
            elif s[0]=='-':
                potential_suffix.append(s[0])
                potential_suffix.append(s[-1])
                
            ### if character has plus before it (most likely mistake or bug)
            elif s[0]=='+': 
                potential_suffix.append(s[0])
                potential_suffix.append(s[-1])
                
        # Check if not contains +
        ### if + is not in the list in a list, then merge as one string and append it to be an element in the main list
        if '+' not in potential_suffix:
            potential_suffix = list(filter(lambda a: a != "-", potential_suffix))
            potential_suffix = ''.join(potential_suffix)
        dif_suffixes.append(potential_suffix)
        
    return dif_suffixes

def compound_split(file, data):
    """
    German compound word splitter - uses a python module to split up German compound words 
    (for instance the famous Donaudampfschifffahrtskapitänsmützenabzeichen). 
    
    Citation: 
    german_compound_splitter, Copyright 2020 by repodiac, see https://github.com/repodiac for updates and further information
    
    Returns list of dissected words.
    
    file = Large reference file consisting of many german words.
    data = list of words to be split.
    """
    
    ahocs = comp_split.read_dictionary_from_file(get_file.compound_splitter_filepath)
    dissected_words = []
    
    with contextlib.redirect_stdout(io.StringIO()):
        for wrd in data:
            try:
                dissection = comp_split.dissect(wrd, ahocs, make_singular = False, only_nouns=False)
                dissected_words.append(dissection)
            except:
                dissected_words.append("ERROR")
            
    return dissected_words

def compound_split_large(file, large_list):
    """
    German compound word splitter - uses a python module to split up German compound words 
    (for instance the famous Donaudampfschifffahrtskapitänsmützenabzeichen). 
    
    Citation: 
    german_compound_splitter, Copyright 2020 by repodiac, see https://github.com/repodiac for updates and further information
    
    Returns list of dissected words.
    
    file = Large reference file consisting of many german words.
    large_list = list of words to be split from large list.
    """
    
    large_dissected_words = []
    
    with contextlib.redirect_stdout(io.StringIO()):
        for wrd in get_file.german_basic_word_list:
            try:
                dissection_large = comp_split.dissect(wrd, get_file.compound_splitter_filepath, make_singular = False, only_nouns=False)
                large_dissected_words.append(dissection_large)
            except:
                large_dissected_words.append("ERROR")
            
    return large_dissected_words

def compound_large(large_list):
    """
    Function for the cistem stemming of words from the large list of words.
    Returns list of stemmed words
    
    large_list = list of words from the large text file
    """
    
    german_larger_cistem = []
    
    large_german_str = [str(i) for i in get_file.german_basic_word_list]
    
    for word in large_german_str:
        cistem_stemmer_large = Cistem().segment(word)
        german_larger_cistem.append(list(cistem_stemmer_large))
        
    return german_larger_cistem

def result(data, pickle_it=False):
    """
    Function for getting the affixes and their zipf frequencies.
    Returns a print out of suffixes with the zipf frequencies and saves them as a text file and potentially as a pickled file.
    
    data = list of words
    pickle_it = set to True if you want the result pickled for further use
    """   
    sb_stem = sb_stemming(data)
    cistem_stem = cistem_stemmeing(data)
    differences = stem_differences(data, sb_stem)
    subtlex_compound_split = compound_split(get_file.compound_splitter_filepath, data)
    comp_split_large = compound_split_large(get_file.compound_splitter_filepath, get_file.german_basic_word_list)
    comp_large = compound_large(get_file.german_basic_word_list)
    
    # Cell general storage
    suffix = []
    prefix = []
    suffix_dict = {}
    prefix_dict = {}
    suffix_freq = []
    prefix_freq = []
    
#______________________________________________________________________________________________________
    
    # dissected subtlex
    list_dissected_subtlex = []
    list_dissected__substlex_cistem = []
    
    for l in subtlex_compound_split:
        for wrd in l:
            list_dissected_subtlex.append(wrd)

    for word in list_dissected_subtlex:
        cistem_stemmer_dissected = Cistem().segment(word)
        list_dissected__substlex_cistem.append(list(cistem_stemmer_dissected))

#______________________________________________________________________________________________________

    ## dissected large german vocab
    list_dissected_large = []
    list_dissected__large_cistem = []

    for l in comp_split_large:
        for wrd in l:
            list_dissected_large.append(wrd)

    for word in list_dissected_large:
        cistem_stemmer_dissected_large = Cistem().segment(word)
        list_dissected__large_cistem.append(list(cistem_stemmer_dissected_large))

#_______________________________________________________________________________________________________

# Stemmed words
    for list_ in cistem_stem:
        list_ = list(filter(None, list_))
        # suffix
        if len(list_) > 1 and len(list_[1]) < len(list_[0]):
            suffix.append(list_[1])
        # prefix
        elif len(list_) > 1 and len(list_[0]) < len(list_[1]):
            prefix.append(list_[0])
    
    # SUBTLEX dissected words
    for list_ in list_dissected__substlex_cistem:
        list_ = list(filter(None, list_))
        # suffix
        if len(list_) > 1 and len(list_[1]) < len(list_[0]):
            suffix.append(list_[1])
        # prefix
        elif len(list_) > 1 and len(list_[0]) < len(list_[1]):
            prefix.append(list_[0])

    # Large german vocab dissected words
    for list_ in list_dissected__large_cistem:
        list_ = list(filter(None, list_))
        # suffix
        if len(list_) > 1 and len(list_[1]) < len(list_[0]):
            suffix.append(list_[1])
        # prefix
        elif len(list_) > 1 and len(list_[0]) < len(list_[1]):
            prefix.append(list_[0])

    # Difference
    for suf in differences:
        if type(suf) is str and len(suf) > 0:
            suffix.append(suf)
            
    # Large german vocab cistem
    for list_ in comp_large:
        if len(list_) > 1 and len(list_[1]) < len(list_[0]):
            suffix.append(list_[1])
        elif len(list_) > 1 and len(list_[0]) < len(list_[1]):
            prefix.append(list_[0])

    # Manually add suffixes
    a = 'chen, lein, ismus, ist, istin, nis, nisse, ologie, kunde, tät, ität, erin, ler, lerin, erlin, erei, ant, antin, är, ärin, entin, eur, eurin, euse, ling, öse, or, orin, ator, schaft, tum, art, sorte, sal, sel, wesen, zeug, artig, bar, erlei, fach, fältig, mal, malig, haft, haftig, iv, los, leer, arm, frei, mäßig, gemäß, reich, voll, sam, wert, würdig'
    to_add_suf = a.split(', ')
    
    for i in to_add_suf:
        suffix.append(i)
    
    set_suffixes = set(suffix)
    set_prefixes = set(prefix)
    list_suffix = list(set_suffixes)
    list_prefix = list(set_prefixes)
    
    # suffix freq
    for word_s in list_suffix:
        p_f_s = zipf_frequency(word_s, 'de')
        suffix_freq.append(p_f_s)
        
    # suffix dict
    for word in list_suffix:
        for freq in suffix_freq:
            suffix_dict[word] = freq
            suffix_freq.remove(freq)
            break

    # prefix freq
    for word_p in list_prefix:
        p_f_p = zipf_frequency(word_p, 'de')
        prefix_freq.append(p_f_p)

    # prefix dict
    for word in list_prefix:
        for freq in prefix_freq:
            prefix_dict[word] = freq
            prefix_freq.remove(freq)
            break
    
    suffix_results_dict = {x:y for x,y in suffix_dict.items() if y != 0}
    prefix_results_dict = {x:y for x,y in prefix_dict.items() if y != 0}
    
    with open('german_suffixes_with_frequency.txt', 'w') as suff_file:
        for key, value in suffix_results_dict.items():
            suff_file.write('%s:%s\n' % (key, value))
#     with open('german_prefixes_with_frequency.txt', 'w') as pref_file:
#         for key, value in prefix_results_dict.items():
#             pref_file.write('%s:%s\n' % (key, value))
    
    if pickle_it == True:
        with open('pickled_suffixes', 'wb') as f:
            pickle.dump(suffix_results_dict, f)
#         with open('pickled_prefixes', 'wb') as f_a:
#             pickle.dump(prefix_results_dict, f_a)
            
    return pp.pprint(suffix_results_dict)
