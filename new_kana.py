#重畳型
import MeCab
import json
import urllib.parse
import urllib.request
import spacy
import itertools
import unicodedata
import string
import itertools as it
import os
from pprint import pprint
from string import digits
import itertools
import numpy as np
import re
import gensim
from gensim.models import KeyedVectors

#chiVeのモデル
model = gensim.models.KeyedVectors.load("./chive-1.2-mc5_gensim/chive-1.2-mc5.kv")

#ja_ginzaのロード
nlp = spacy.load('ja_ginza')

#分かち書き
wakati = MeCab.Tagger("-Owakati")

#かな漢字変換
def mecab_list(text):
    tagger = MeCab.Tagger("")
    tagger.parse('')
    node = tagger.parseToNode(text)
    word_class = []
    while node:
        word = node.surface
        wclass = node.feature.split(',')
        if wclass[0] != u'BOS/EOS':
            if wclass[6] == None:
                word_class.append((word,wclass[0],wclass[1],wclass[2],""))
            else:
                word_class.append((word,wclass[0],wclass[1],wclass[2],wclass[6]))
        node = node.next
    return word_class

    
def convert_kata_to_hira(katakana):
    hira_tupple = ('あ','い','う','え','お','か','き','く','け','こ','さ','し','す','せ','そ','た','ち','つ','て','と','な','に','ぬ','ね','の','は','ひ','ふ','へ','ほ','ま','み','む','め','も','や','ゆ','よ','ら','り','る','れ','ろ','わ','を','ん','っ','ゃ','ゅ','ょ','ー','が','ぎ','ぐ','げ','ご','ざ','じ','ず','ぜ','ぞ','だ','ぢ','づ','で','ど','ば','び','ぶ','べ','ぼ','ぱ','ぴ','ぷ','ぺ','ぽ','ぁ','ぃ','ぅ','ぇ','ぉ')
    kata_tupple = ('ア','イ','ウ','エ','オ','カ','キ','ク','ケ','コ','サ','シ','ス','セ','ソ','タ','チ','ツ','テ','ト','ナ','ニ','ヌ','ネ','ノ','ハ','ヒ','フ','ヘ','ホ','マ','ミ','ム','メ','モ','ヤ','ユ','ヨ','ラ','リ','ル','レ','ロ','ワ','ヲ','ン','ッ','ャ','ュ','ョ','ー','ガ','ギ','グ','ゲ','ゴ','ザ','ジ','ズ','ゼ','ゾ','ダ','ヂ','ヅ','デ','ド','バ','ビ','ブ','ベ','ボ','パ','ピ','プ','ペ','ポ','ァ','ィ','ゥ','ェ','ォ')
    k_to_h_dict = dict()
    for i in range(len(hira_tupple)):
        k_to_h_dict[kata_tupple[i]] = hira_tupple[i]
    hiragana = ""
    for i in range(len(katakana)):
        hiragana += k_to_h_dict[katakana[i]]
    return hiragana



def new_kana(dajare):
    test = dajare
    detected = '失敗'
    tane = 'なし'
    senzai = 'なし'
    henkei = 'なし'
    sim = 0
        
    #print('=====================================================================================')
    #print()
    t_lst = []
    #print('駄洒落文：' + dajare)
    dajare = dajare.replace('～','ー')
    dajare = dajare.replace('~','ー')
    dajare = dajare.replace('♪','')
    doc = nlp(dajare)
    punct_non_text = ""
    for token in doc:
        if token.is_punct == False:
            punct_non_text = punct_non_text + token.text
    word=punct_non_text
    #print(word)
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
                tk_lst.append(token.morph.get("Reading")[0])
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
    #print()

    re_k = re.compile(r'^[\u30A0-\u30FFー]+$')

    for x in range(len(tk_lst)):

        if tk_lst[x]:
            #print("種表現：",tk_lst[x])
            #print("tk_lst[x]:",tk_lst[x])
            if re_k.match(tk_lst[x]):
                tane_kana = convert_kata_to_hira(tk_lst[x])

                url = "http://www.google.com/transliterate?"
                param = {'langpair':'ja-Hira|ja','text':tane_kana}
                paramStr = urllib.parse.urlencode(param)
                ##print(url + paramStr)
                readObj = urllib.request.urlopen(url + paramStr)
                response = readObj.read()
                data = json.loads(response)
                fixed_tane_data = json.loads(json.dumps(data[0], ensure_ascii=False))

                for y in range(len(henkei_lst)):
                    #print("変形表現元：",henkei_lst[y])
                    if all(num not in tk_number_lst[x] for num in henkei_element_used[y]):
                        if henkei_lst[y][0] not in ['ャ','ュ','ョ','ァ','ィ','ゥ','ェ','ォ']:
                            henkei_length = len(henkei_lst[y])
                            if henkei_lst[y] in ['ャ','ュ','ョ','ァ','ィ','ゥ','ェ','ォ']:
                                henkei_length = henkei_length - 1
                            if henkei_length >= 2:
                                if re_k.match(henkei_lst[y]):
                                    henkei_kana = convert_kata_to_hira(henkei_lst[y])
                                    #print("henkei_kana:",henkei_kana)
                                    param = {'langpair':'ja-Hira|ja','text':henkei_kana}
                                    paramStr = urllib.parse.urlencode(param)
                                    ##print(url + paramStr)
                                    readObj = urllib.request.urlopen(url + paramStr)
                                    response = readObj.read()
                                    data = json.loads(response)
                                    fixed_henkei_data = json.loads(json.dumps(data[0], ensure_ascii=False))
                                    
                                    #print("種表現カナ漢字変換：",fixed_tane_data)
                                    for s in range(len(fixed_tane_data[1])):
                                        #print("変形表現カナ漢字変換：",fixed_henkei_data)
                                        for h in range(len(fixed_henkei_data[1])):
                                            if fixed_tane_data[1][s] != fixed_henkei_data[1][h]:
                                                if fixed_tane_data[1][s] in model:
                                                    if fixed_henkei_data[1][h] in model:
                                                        #コサイン類似度を計算
                                                        cos =float(model.similarity(fixed_tane_data[1][s], fixed_henkei_data[1][h]))

                                                        if cos > 0.6:
                                                            #print("閾値0.6")
                                                            print("種表現:", tane_kana, "の漢字変換候補：", fixed_tane_data[1])
                                                            print(tane_kana, " ==> ", fixed_tane_data[1][s]," に変換" )
                                                            print("変形表現", henkei_lst[y], "の漢字変換候補：", fixed_henkei_data[1])
                                                            print(henkei_lst[y], " ==> ", fixed_henkei_data[1][h], " に変換")
                                                            print(fixed_tane_data[1][s],"と",fixed_henkei_data[1][h],"のコサイン類似度：",cos)
                                                            print('\033[32m'+ '検出成功' +'\033[0m')
                                                            detected = "成功"
                                                            tane = t_lst[x]
                                                            senzai = fixed_tane_data[1][s]
                                                            henkei = fixed_henkei_data[1][h]
                                                            sim = cos
                                                            return detected, tane, senzai, henkei, sim
                          
    return detected, tane, senzai, henkei, sim