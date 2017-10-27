from __future__ import division
try:
	import json
except ImportError:
	import simplejson as json
from pprint import pprint
from dateutil.parser import parse
from dateutil.tz import *
from datetime import *
import ast
import re
import sys
import time
import os
import nltk, re, pprint, string
from nltk import word_tokenize
from nltk.tokenize import WordPunctTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.metrics import edit_distance
import enchant

def printKey(dictionary, key, depth = 0):
	print "\t" * depth + key
	if isinstance(dictionary[key], dict):
		for subkey in dictionary[key]:
			printKey(dictionary[key], subkey, depth + 1)

def sameletters(s1, s2):
	s1 = re.sub(r'(.)\1+', r'\1', s1)
	s2 = re.sub(r'(.)\1+', r'\1', s2)
	return s1 == s2

def asciiSpell(word):
	spell_dict = enchant.Dict('en_US')
	max_dist = 2
	if spell_dict.check(word):
		return word
	suggestions = sorted(spell_dict.suggest(word), key=lambda sugg: edit_distance(sugg, word) * 0 if sameletters(word, sugg) else 1)
	if edit_distance(suggestions[0], word) <= max_dist:
		return suggestions[0]
	return word

def spell(words):
	spelled = []
	for word in words:
		try:
			spelled.append(asciiSpell(re.sub(r'(.)\1+', r'\1\1', str(word))))
		except UnicodeEncodeError:
			pass
	return spelled

def removeEntities(text, entities = None):
	text = re.sub(r'http\S+', '', text)
	if entities is not None:
		for entityType in entities:
			if entityType == "user_mentions":
				for i in xrange(len(entities[entityType])):
					text = text.replace(entities[entityType][i]["screen_name"], '')
			elif entityType == "urls":
				for i in xrange(len(entities[entityType])):
					for both in ["url", "expanded_url"]:
						text = text.replace(entities[entityType][i][both], '')
	text = re.sub(r'\&\S+;', '', text)
	return text.replace("#", '')

def removePunctuation(text):
	regex = re.compile('[%s]' % re.escape(string.punctuation))
	return regex.sub(' ', text)

def lemmatize(text):
	word_punct_tokenizer = WordPunctTokenizer()
	tokens = word_punct_tokenizer.tokenize(text)
	lem = WordNetLemmatizer()
	ps = PorterStemmer()
	return [lem.lemmatize(w.lower()) for w in tokens] # [lem.lemmatize(ps.stem(w.lower())) for w in tokens]

def removeStopwords(words):
	return list(filter(lambda word: word not in stopwords.words('english'), words))

def process(tweet):
	tweet = json.loads(tweet)
	text = removeEntities(tweet["text"], tweet["entities"])
	text = removePunctuation(text)
	words = lemmatize(text)
	words = removeStopwords(words)
	spelled = spell(words)
	return spelled

with open("sampleTweet", "r") as sampleTweet:
	for tweet in sampleTweet:
		processed = process(tweet)
		print processed
