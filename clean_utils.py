import re
import string
import pandas as pd
from cleantext import clean
import os
import requests 
import pandas as pd 
import time
import itertools
import networkx as nx
import string

# NLTK tools
import nltk
nltk.download('words')
words = set(nltk.corpus.words.words())
nltk.download('stopwords')
stop_words = nltk.corpus.stopwords.words("english")
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import pos_tag
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')
from collections import defaultdict
tag_map = defaultdict(lambda : wn.NOUN)
tag_map['J'] = wn.ADJ
tag_map['V'] = wn.VERB
tag_map['R'] = wn.ADV




# Functions to create clean text for the LIWC analysis
def remove_hashtag(match_obj):
    if match_obj.group() is not None:
        return match_obj.group()[1:]

def remove_quotation(match_obj):
    if match_obj.group() is not None:
        return match_obj.group()[1:]


def tweet2text(tweet):
    tweet = re.sub("@[A-Za-z0-9_]+","",tweet) # remove mentions
    tweet = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet) # remove http links
    tweet = re.sub("[A-Za-z0-9_]+.com","",tweet)
    tweet = re.sub(" \'s", ' ', tweet) # remove 's that have been left out after deleting mentions
    tweet = re.sub("^\'s", ' ', tweet)
    tweet = re.sub("#[A-Za-z0-9]+", remove_hashtag, tweet) # remove hashtag symbol
    tweet = re.sub('\([0-9s]\)', ' ', tweet) # remove added (1) to number tweets or (s) to make optional plural
    tweet = re.sub('&amp', ' ', tweet)
    tweet = str.lower(tweet) #to lowercase
    tweet = re.sub('-d', 'd', tweet) # Some people add -d to hashtags to make it past while keeping the hashtag (eg: #rape-d)
    tweet = re.sub('^rt', '', tweet)

    # Remove repeated ! and ? and no needed puntuation marks
    tweet = re.sub('\?{2,}', "?", tweet)
    tweet = re.sub('!{2,}', "!", tweet)
    tweet = re.sub('[*+\"\(\)/]', ' ', tweet)
    
    # Common shortenings
    tweet = re.sub(' u ', ' you ', tweet)
    tweet = re.sub(' r ', ' are ', tweet)
    tweet = re.sub(' @ ', ' at ', tweet)
    tweet = re.sub('&', 'and', tweet)
    tweet = re.sub(' ur ', 'your', tweet)
    tweet = re.sub(' w/ ', ' with ', tweet)

    # Remove emojis
    # Final cleanup: correct spelling mistakes, no emojis, no phone numbers or emails, ...
    tweet = clean(tweet, fix_unicode=True, to_ascii=True, lower=True, normalize_whitespace=True, 
                  no_line_breaks=True, no_emails=False, no_phone_numbers=True, no_emoji=True,
                  replace_with_phone_number='phone number')
    tweet = re.sub('^[.]+', '', tweet) #remove dots at the beggining of string
    #tweet = " ".join(tweet.split())
    return tweet


# Function to create clean text for extracting words - get read of irrelevant ones
def cleaner(tweet):
    tweet = re.sub("@[A-Za-z0-9]+","",tweet) # remove mentions
    tweet = re.sub("#[A-Za-z0-9]+", "",tweet) # remove hashtags
    tweet = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet) # remove http links
    tweet = " ".join(tweet.split())
    tweet = " ".join(w for w in nltk.wordpunct_tokenize(tweet) if w.lower() in words and not w.lower() in stop_words)
     #remove stop words
    lemma_function = WordNetLemmatizer()
    tweet = " ".join(lemma_function.lemmatize(token, tag_map[tag[0]]) for token, tag in nltk.pos_tag(nltk.wordpunct_tokenize(tweet))) #lemmatize
    tweet = str.lower(tweet) #to lowercase
    return tweet