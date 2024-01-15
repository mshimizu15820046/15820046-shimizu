#重畳型
import MeCab
import gensim
import unicodedata
import string
import itertools as it
import os
import editdistance as ed
import distanceutil
import similarity
import Levenshtein as ls
from pprint import pprint
from string import digits
import spacy
from gensim.models import KeyedVectors
import pykakasi

import requests
import json


model_dir = './entity_vector.model.bin'
model = KeyedVectors.load_word2vec_format(model_dir, binary=True)

#ja_ginzaのロード
nlp = spacy.load('ja_ginza')

#分かち書き
wakati = MeCab.Tagger("-Owakati")

kks = pykakasi.kakasi()


import re
def format_text(text):
    text=re.sub('、', "", text)
    text=re.sub('？', "", text)
    text=re.sub('！', "", text)
    text=re.sub('は', "", text)
    text=re.sub('が', "", text)
    text=re.sub('の', "", text)
    text=re.sub('に', "", text)
    text=re.sub('と', "", text)
    text=re.sub('を', "", text)
    return text


def new_entity(dajare):
    lines = dajare
    detected = '失敗'
    tane = 'なし'
    senzai = 'なし'
    henkei = 'なし'
    sim = 0
    t_lst = []
    
    #print('=====================================================================================')
    #print()
    print('駄洒落文：' + dajare)
    doc = nlp(dajare)
    punct_non_text = ""
    for token in doc:
        if token.is_punct == False:
            punct_non_text = punct_non_text + token.text
    word = punct_non_text
    print(word)
    doc = nlp(word)
    yomi_lst = []
    yomi_len_lst = []
    for token in doc:
        yomi_lst.append(token.morph.get("Reading"))
    for i in yomi_lst:
        if not i:
            continue
        yomi_len_lst.append(len(str(i))-4)

    yomi_number_lst = [[] for _ in range(len(yomi_len_lst))]
    
    current_index = 0
    for i, length in enumerate(yomi_len_lst):
        yomi_number_lst[i] = list(range(current_index, current_index + length))
        current_index += length

    token_flag = 0
    tk_lst = []
    tk_elements_lst = []
    for token in doc:
        if not token.is_space:
            if token.pos_ in ["NOUN", "PROPN", "VERB"]:
                t_lst.append(token.text)
                tk_lst.append(token.morph.get("Reading"))
                tk_elements_lst.append(token_flag)
            token_flag = token_flag + 1
    tk_number_lst = []
    for i in tk_elements_lst:
        tk_number_lst.append(yomi_number_lst[i])

    text = ""
    for i in yomi_lst:
        mora_text = str(i).replace("'","")
        mora_text = mora_text.replace("[","")
        mora_text = mora_text.replace("]","")
        text += mora_text
    
    henkei_lst = []
    henkei_element_used = []

    for i in range(len(text)):
        for j in range(i, len(text)):
            substring = text[i:j+1]
            henkei_lst.append(substring)
            elements_used = [k for k in range(i, j+1)]
            #print(elements_used)
            henkei_element_used.append(elements_used)
    
    #henkei_elements_usedから''を削除
    henkei_elements_used = [[int(element) for element in sub_list] for sub_list in henkei_element_used]

    #print("yomi_lst:",yomi_lst)
    #print("text:",text)
    #print("種表現候補:",t_lst)
    #print("種表現のエレメント:",tk_number_lst)
    #print("変形表現候補:",henkei_lst)
    #print("変形表現のエレメント:",henkei_element_used)
    print()
    for x in range(len(t_lst)):
        
        #類似度が高い上位500件かつ値が0.4以上の単語を取得
        if t_lst[x] in model.key_to_index:
            similar_words=model.most_similar(t_lst[x], topn=500)
            #print("種表現:",t_lst[x])
            #print("種表現のエレメント:",tk_number_lst)
            #print("潜在表現候補:",similar_words)
            for y in range(len(similar_words)):
                if float(similar_words[y][1]) >= 0.6:

                    text1=similar_words[y][0]
                    result = kks.convert(text1)
                    text2 = ''.join([item['kana'] for item in result])
                    #print("text2:",text2)
                    #pprint(similar_words[y])

                #類似度が高い単語と駄洒落文中の単語の音韻類似度を計算
                #種表現と変形表現のジャロウィンクラー距離が0.8未満のときのみ(併置型駄洒落) 
                    for z in range(len(henkei_lst)):
                        if all(num not in tk_number_lst[x] for num in henkei_element_used[z]):
                            if henkei_lst[z][0] not in ['ャ','ュ','ョ','ァ','ィ','ゥ','ェ','ォ']:
                                henkei_length = len(henkei_lst[z])
                                if henkei_lst[z] in ['ャ','ュ','ョ','ァ','ィ','ゥ','ェ','ォ']:
                                    henkei_length = henkei_length - 1
                                if henkei_length >= 2:
                                    if ls.jaro_winkler(tk_lst[x],henkei_lst[z]) < 0.5:
                                        jaro = ls.jaro_winkler(text2,henkei_lst[z])
                                        if jaro >= 0.95:
                                            detected = "成功"
                                            if sim < jaro:
                                                print("種表現:",t_lst[x],"潜在表現:",text2,"変形表現:",henkei_lst[z],"類似度:",jaro)
                                                tane = t_lst[x]
                                                senzai = text2
                                                henkei = henkei_lst[z]
                                                sim = jaro

    return(detected, tane, senzai, henkei, sim)

