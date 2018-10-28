#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is for generate soundex dictionary
"""
from pypinyin import  lazy_pinyin
import jieba

def isAllChinese(s):
    for c in s:
        if not('\u4e00' <= c <= '\u9fa5'):
            return False
    return True


                    
def pinyinphrase(text):
    code_dict={}
    cicode=''
    for i in text:
            i = i.strip()
            seg_text = ' '.join(jieba.cut(i))
            seg_text = seg_text.split()
            try:
                pinyin_phrase = [lazy_pinyin(i) for i in seg_text ]
            except Exception as e:
                print (i,Exception,",",e)
#            print (pinyin_phrase)
#            data.write(str(pinyin_phrase))
#            data.write('\n')
#            data.write(str(seg_text))
#            data.write('\n')
            for ci,i in zip(pinyin_phrase,seg_text):
                for zi in ci:
                    if zi.isalpha() :   #除去数字
                        try:
                            if len(zi) == 1:
                                code = soundex[zi]+'0000'
                            elif len(zi) == 2:
                                if zi in soundex.keys():
                                    code = soundex[zi]+'0000'
                                else:
                                    code = soundex[zi[0]]+'00'+soundex[zi[1]]
                            elif len(zi) >= 3:
            #                        声母音标
                                code = soundex[zi[0]]
            #                        声母为一个字符的
                                if zi[:2] not in ['zh','sh','ch']:
            #                            有第二音节
                                    if (zi[1] == 'i' or zi[1] == 'u') and (zi[1:3] not in ['iu','ie','in','ui','un']):
                                        code = code + soundex[zi[1]]+ soundex[zi[2:]]
#                                        ang,eng,ing,ong
                                    elif zi in soundex.keys():
                                        code = soundex[zi]+'0000'
            #                            无第二音节
                                    else:
                                        code = code +'00'+soundex[zi[1:]]
            #                                print (i,code)
            #                       声母为两个字符的
                                else:
            #                            长度为3则无中间音节
                                    if len(zi) == 3:
                                        code = code + '00' + soundex[zi[-1]]
            #                            长度大于3判断有无中间音节
                                    else:
            #                                有第二音节
                                        if (zi[2] == 'i' or zi[2] == 'u') and (zi[2:4] not in ['iu','ie','in','ui','un']):
                                            code = code + soundex[zi[2]]+soundex[zi[3:]]
            #                                无第二音节
                                        else:
                                            code = code+'00'+soundex[zi[2:]]
        #                    print (zi,code)
                            cicode += code
                        except Exception as e:
                            print (i,Exception,",",e)
#                print (i,cicode)
                if len(cicode)>1 and isAllChinese(i) == True:
#                    如果新词的编码已经存在但新词并不存在
                    if cicode in code_dict.keys() and i not in code_dict[cicode] :
#                        print (code_dict[cicode],i)
#                        data.write(str(code_dict[cicode])+str(i)+str(ci))
#                        data.write('\n')
                        code_dict[cicode].append(i)
                    elif cicode not in code_dict.keys():
                        code_dict[cicode]=[i]
#                        data.write(str(code_dict[cicode])+str(i)+str(ci))
#                        data.write('\n')
                cicode=''
    return code_dict
                        
soundex={}
code = ''
with open('cidian/only_words_new.txt', encoding = 'utf-8') as wrong:
    with open('cidian/soundex_rule.txt',encoding = 'utf-8') as sound:
        with open('cidian/soundex_code_new.txt','w',encoding = 'utf-8') as data:
            for i in sound.readlines():
                i = i.split()
                soundex[i[0]] = i[1]

            
            text = wrong.readlines()
            code_dict = pinyinphrase(text)
            for k,v in code_dict.items():
                data.write(str(k)+'\t'+str('\t'.join(v)))
                data.write('\n')

                        