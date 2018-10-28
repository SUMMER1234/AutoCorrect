#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 10:30:44 2018
author： summer_smx

This file is for checkinxg wrong text and correcting it automatically
"""
from sklearn.feature_extraction.text import CountVectorizer
import json
import math
import time
import jieba
import pickle
import copy
from pypinyin import  lazy_pinyin
from sklearn import svm
import numpy



class checker():
    
    def __init__(self):
        self.p_unigram = 0
        self.p_bigram = 0
        self.p_trigram = 0
        self.f_dict = {}
        self.data = self.load_data()
        self.total_words = 100000
        self.first_wrong=[]
        self.second_wrong =[]
        self.third_wrong=[]
        self.one_gram = self.onegram()
        self.two_gram = self.twogram()
        self.soundex_dict = self.soundexdict()
        self.soundex_rule = self.load_soundex_rule()
        self.stopwords=['的','有','当','是','在','最佳','最','很','非常','我','你','他','家','还','最近','其实','了','啊','吧','说']
        self.punctuation = '！？？｡＂＃＄％＆＇（）＊＋, ，,－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。'


    def load_data(self):
        # load dictionary
        start = time.clock()
        with open('dict/check_dict.pkl','rb') as pk:
            data = pickle.load(pk)
        end = time.clock()
        print('load: %s seconds' % (end - start))
        return data


    def load_soundex_rule(self):
        # load soundex rule for generate soundex code
        soundex={}
        with open('dict/soundex_rule.txt', encoding='utf-8') as sound:
            for i in sound.readlines():
                i = i.split()
                soundex[i[0]] = i[1]
        return soundex


    def onegram(self):
        # save unigram dict
        uni = self.data['onegram']
        return uni


    def twogram(self):
        # save bigram dict
        bi = self.data['twogram']
        return bi


    def threegram(self):
        # save trigram dict
        tri = self.data['threegram']
        return tri


    def soundexdict(self):
        # save soundex dict
        sou = self.data['soundex']
        return sou


    def input_vec(self,text):
        # get n-gram from input text
        input_vectorizer = CountVectorizer(ngram_range=(1, 2), decode_error="ignore", token_pattern=r'\b\w+\b',
                                           min_df=1)
        x2 = input_vectorizer.fit_transform(text)
        return input_vectorizer, x2


    def jieba_cut(self,sentence):
        #tokenize chinese text
        cut = jieba.cut(sentence)
        result = ' '.join(cut)
        return result


    def split_sentence(self,text):
        # split sentence to avoid generate wrong bigrams
        # (bigrams will skip a punctuation and connect the word before it and the word after it)
        lines=[]
        l=''
        for n,i in enumerate(text):
            l=l+i
            if i in self.punctuation :
                lines.append(l[:-1])
                l=''
            elif n ==len(text) -1:
                lines.append(l)
        return lines


    def find(self,text):
        # generate the frequency dict of ngrams from input text
        lines = self.split_sentence(text)
        for l in lines:
            seg_text = self.jieba_cut(l)
            input_vecorizer, x2 = self.input_vec([seg_text])
            for i in input_vecorizer.vocabulary_.keys():
                try:
                    if len(i.split()) == 1:
                        self.f_dict[i] = self.one_gram[i]
                    elif len(i.split()) == 2:
                        j = '_'.join(i.split())
                        self.f_dict[i] = self.two_gram[j]
                    # elif len(i.split()) == 3:
                    #     j = '_'.join(i.split())
                    #     self.f_dict[i] = self.three_gram[j]
                except Exception as e:
                    self.f_dict[i] = 0
        return self.f_dict


    def n_gram(self,k,v):
        try:
            if len(k.split()) ==1:
                self.p_unigram = int(self.f_dict[k])/self.total_words
                # print(k + '\t' + 'p_unigram:' + '\t' + str(self.p_unigram))
                if self.p_unigram == 0.0:
                    self.first_wrong.append(k)
            if len(k.split()) == 2:
                self.p_bigram = int(v) / int(self.f_dict[k.split()[0]])
                # print (k + '\t'+'p_bigram:'+'\t'+ str(self.p_bigram))
                if self.p_bigram == 0.0 or self.p_bigram == 0:
                    self.second_wrong.append(k)
            # if len(k.split()) == 3:
            #     self.p_trigram = int(v) / int(self.f_dict[' '.join(k.split()[:2])])
            #     # print (k + '\t'+ ' p_trigram: '+ '\t' + str(self.p_trigram))
            #     if self.p_trigram == 0.0 or self.p_trigram == 0:
            #         self.third_wrong.append(k)
        except Exception as e:
            # print(k, Exception, ":", e)
            if len(k.split()) == 2:
                self.p_bigram = 0
                # print(k + '\t'+ ' p_bigram: ' + '\t'+ str(self.p_bigram))
                self.second_wrong.append(k)
            if len(k.split()) == 3:
                self.p_trigram = 0
                # print(k + '\t'+ ' p_trigram: ' + '\t'+ str(self.p_trigram))
                self.third_wrong.append(k)


    def mutual_info_cal(self,x, y, xy,):
        # mutual infomation formula
        p_x = x / self.total_words
        log_x = math.log(p_x)
        p_xy = xy / y
        log_xy = math.log(p_xy)
        mi = -p_x * log_x - (-p_xy * log_xy)
        return mi


    def mi(self,k,v):
        # calculate 2grams mi
        try:
            if len(k.split()) == 2:
                x = k.split()[0]
                y = k.split()[1]
                mi = self.mutual_info_cal(int(self.f_dict[x]), int(self.f_dict[y]), int(v))
                # print(str(k) + '\t' + 'MI:' + '\t' + str(mi))
        except Exception as e:
            # print(k, Exception, ":", e)
            # print(str(k) + '\t' + 'MI:' + '\t' + 'two words are not matching')
            mi = 0
        return mi


    def wrong_candidates(self,text):
        #get one words wrong candidates and two words wrong candidates
        self.f_dict = self.find(text)
        for k, v in self.f_dict.items():
            self.n_gram(k,v)
            # self.mi(k,v)
        self.f_dict = {}
        return self.first_wrong, self.second_wrong


    def check_twogram(self):
        # filter wrong two words candidates
        # start = time.clock()
        temp = copy.deepcopy(self.second_wrong)
        for i in self.second_wrong:
            if i.split()[0] in self.stopwords or i.split()[1] in self.stopwords:
                temp.remove(i)

        #     三元共现且其中二元可以组合成一个在一元中的词，则将此三元组合中另外一个组合删掉
        for i in self.third_wrong:
            x = i.split()[0]+i.split()[1]
            y = i.split()[1]+i.split()[2]
            if x in self.one_gram.keys() or y in self.one_gram.keys():
                # print(x,y)
                if i.split()[0] + ' ' + i.split()[1] in temp:
                    temp.remove(i.split()[0] + ' ' + i.split()[1])
                if i.split()[1] + ' ' + i.split()[2] in temp:
                    temp.remove(i.split()[1] + ' ' + i.split()[2])

        self.second_wrong=temp
        # end = time.clock()
        # print('check: %s seconds' % (end - start))
        return self.second_wrong


    def edits1(self,phrase):
        # calculate edit distance
        # start = time.clock()
        splits = [(phrase[:i], phrase[i:]) for i in range(len(phrase) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        # deletes2 = [L + R[2:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in self.one_gram.keys()]
        inserts = [L + c + R for L, R in splits for c in self.one_gram.keys()]
        # end = time.clock()
        # print('edits: %s seconds' % (end - start))
        return set(deletes  + transposes + replaces + inserts)


    def soundex(self,phrase):
        # rule of generate soundex code
        # start = time.clock()
        cicode = ''
        pinyin = lazy_pinyin(phrase)
        for zi in pinyin:
            if zi.isalpha():  # 除去数字
                try:
                    if len(zi) == 1:
                        code = self.soundex_rule[zi] + '0000'
                    elif len(zi) == 2:
                        if zi in self.soundex_rule.keys():
                            code = self.soundex_rule[zi] + '0000'
                        else:
                            code = self.soundex_rule[zi[0]] + '00' + self.soundex_rule[zi[1]]
                    elif len(zi) >= 3:
                        #  声母音标
                        code = self.soundex_rule[zi[0]]
                        #  声母为一个字符的
                        if zi[:2] not in ['zh', 'sh', 'ch']:
                            #  有第二音节
                            if (zi[1] == 'i' or zi[1] == 'u') and (zi[1:3] not in ['iu', 'ie', 'in', 'ui', 'un']):
                                code = code + self.soundex_rule[zi[1]] + self.soundex_rule[zi[2:]]
                            #  ang,eng,ing,ong
                            elif zi in self.soundex_rule.keys():
                                code = self.soundex_rule[zi] + '0000'
                            #   无第二音节
                            else:
                                code = code + '00' + self.soundex_rule[zi[1:]]
                        #                                print (i,code)
                        #   声母为两个字符的
                        else:
                            #  长度为3则无中间音节
                            if len(zi) == 3:
                                code = code + '00' + self.soundex_rule[zi[-1]]
                            #   长度大于3判断有无中间音节
                            else:
                                #  有第二音节
                                if (zi[2] == 'i' or zi[2] == 'u') and (
                                        zi[2:4] not in ['iu', 'ie', 'in', 'ui', 'un']):
                                    code = code + self.soundex_rule[zi[2]] + self.soundex_rule[zi[3:]]
                                #   无第二音节
                                else:
                                    code = code + '00' + self.soundex_rule[zi[2:]]
                    #                    print (zi,code)
                    cicode += code
                except Exception as e:
                    pass
                    # print(i, Exception, ",", e)
        # end = time.clock()
        # print('soundex: %s seconds' % (end - start))
        return cicode


    def correct_candidates(self):
        # start = time.clock()
        correct_pair={}
        two_words_set=set()
        for i in self.first_wrong:
            temp = set()
            # li = self.edits1(i)
            # temp = copy.deepcopy(li)
            # for l in li:
            #     if l  in self.one_gram.keys():
            #         pass
            #     else:
            #         temp.remove(l)
            code = self.soundex(i)
            if code in self.soundex_dict.keys():
                for x in self.soundex_dict[code]:
                    temp.add(x)
            if len(temp) == 0:
                code = self.soundex(i[:-1])
                if code in self.soundex_dict.keys():
                    for x in self.soundex_dict[code]:
                        temp.add(x)
            correct_pair[i] = temp

        for i in self.second_wrong:
            temp1 = set()
            if i.split()[0] == i.split()[1]:
                two_words_set.add(i.split()[0])
                correct_pair[i] = two_words_set
            two_code=self.soundex(i.split()[0] + i.split()[1])
            if two_code in self.soundex_dict.keys():
                for x in self.soundex_dict[two_code]:
                    temp1.add(x)
            if len(temp1)>0:
                correct_pair[i] = temp1

        # print(correct_pair)
        # end = time.clock()
        # print('correct: %s seconds' % (end - start))
        return correct_pair


    def svm(self,value):
        # ranking method
        X = [[0, 0, 0, 0], [1, 1, 10, 20]]
        y = [0, 1]
        clf = svm.SVC(probability=True)
        clf.fit(X, y)
        value=numpy.array([value])
        label= numpy.array([[1]])
        score = clf.score(value,label)
        return score


    def autocorrect(self,text,out):
        # start = time.clock()
        self.wrong_candidates(text)
        self.check_twogram()
        candidates = self.correct_candidates()
        seg_text = self.jieba_cut(text).split()
        two_grams =[]
        choose_top={}
        for n,i in enumerate(seg_text):
            if n< len(seg_text)-1 and i not in self.punctuation and seg_text[n+1] not  in self.punctuation:
                two = i+' '+seg_text[n+1]
                two_grams.append(two)

        for i in candidates.keys():
            next = []
            if len(candidates[i]) == 1:
                text = text.replace(''.join(i.split()), list(candidates[i])[0])
            if len(candidates[i]) > 1:
                for x in two_grams:
                    if i in x:
                        next.append(x)
                for y in list(candidates[i]):
                    score = []
                    count = 0
                    if len(next)>0:
                        next1=next[0].replace(i,y)
                        # add features for each candidates to rank
                        if next1 in self.two_gram.keys():
                            score.append(self.two_gram[next1])
                        else:
                            score.append(0)
                        if next1 in self.two_gram.keys():
                            mi = self.mi(next1,self.two_gram[next1])
                            score.append(int(mi))
                        else:
                            score.append(0)
                        if lazy_pinyin(i) == lazy_pinyin(y):
                            score.append(10)
                        else:
                            score.append(0)
                        if i[0] == y[0]:
                            count+=10
                        if len(i)>1 and len(y)>1 and i[1] == y[1]:
                            count+=10
                        if len(i)>2 and len(y)>2 and  i[2] == y[2]:
                            count+=10
                        score.append(count)
                        top = self.svm(score)
                        choose_top[y] = top
                        if top == 1 or top == 1.0:
                            choose_top[y] = sum(score)
                            # print(y,sum(score))
            if choose_top:
                change = sorted(choose_top.items(), key=lambda d: d[1],reverse=True)[0][0]
                text = text.replace(''.join(i.split()), change)
            choose_top = {}
        print(text)
#        if out!= 0:
#            out.write(text)
#            out.write('\n')
#        else:
#            pass
        self.first_wrong=[]
        self.second_wrong=[]
        self.third_wrong=[]
        # end = time.clock()
        # print('autocorrect: %s seconds' % (end - start))



if __name__=="__main__":
    ngram = checker()
    # with open('test_wrong.txt',encoding='utf-8') as inp:
    #     with open('output.txt', 'w', encoding='utf-8') as out:
    #         for l in inp.readlines():
    #             l=l.strip()
    out = 0
    l = '杭洲是中国的八大古都之一，因风景锈丽，享有人间天糖的美誉。'
    start = time.clock()
    ngram.autocorrect(l,out)
    end = time.clock()
    print('total: %s seconds' % (end - start))
    
