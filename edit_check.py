#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is for check edit distance
"""
import pickle
import gzip



from pypinyin import  lazy_pinyin, Style

def edits1(phrase):
    "All edits that are one edit away from `phrase`."
#    phrase = phrase.decode("utf-8")
    splits     = [(phrase[:i], phrase[i:])  for i in range(len(phrase) + 1)]
    deletes    = [L + R[1:]                 for L, R in splits if R]
    deletes2   = [L + R[2:]                 for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:]   for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]             for L, R in splits if R for c in cn_words_dict]
    inserts    = [L + c + R                 for L, R in splits for c in cn_words_dict]
#    return transposes
    return set(deletes + deletes2 + transposes + replaces + inserts)


#with open('checker.pickle') as cp:
try:
    f = gzip.open('checker.pickle', 'rb')
    d = pickle.loads(f.read())
except IOError:
    f = open('checker.pickle', 'rb')
    d = pickle.loads(f.read())
f.close()
cn_words_dict = d['words']