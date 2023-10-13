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
    hira_tupple = ('あ','い','う','え','お','か','き','く','け','こ','さ','し','す','せ','そ','た','ち','つ','て','と','な','に','ぬ','ね','の','は','ひ','ふ','へ','ほ','ま','み','む','め','も','や','ゆ','よ','ら','り','る','れ','ろ','わ','を','ん','っ','ゃ','ゅ','ょ','ー','が','ぎ','ぐ','げ','ご','ざ','じ','ず','ぜ','ぞ','だ','ぢ','づ','で','ど','ば','び','ぶ','べ','ぼ','ぱ','ぴ','ぷ','ぺ','ぽ')
    kata_tupple = ('ア','イ','ウ','エ','オ','カ','キ','ク','ケ','コ','サ','シ','ス','セ','ソ','タ','チ','ツ','テ','ト','ナ','ニ','ヌ','ネ','ノ','ハ','ヒ','フ','ヘ','ホ','マ','ミ','ム','メ','モ','ヤ','ユ','ヨ','ラ','リ','ル','レ','ロ','ワ','ヲ','ン','ッ','ャ','ュ','ョ','ー','ガ','ギ','グ','ゲ','ゴ','ザ','ジ','ズ','ゼ','ゾ','ダ','ヂ','ヅ','デ','ド','バ','ビ','ブ','ベ','ボ','パ','ピ','プ','ペ','ポ')
    k_to_h_dict = dict()
    for i in range(len(hira_tupple)):
        k_to_h_dict[kata_tupple[i]] = hira_tupple[i]
    hiragana = ""
    for i in range(len(katakana)):
        hiragana += k_to_h_dict[katakana[i]]
    return hiragana



def kana(dajare):
        test = dajare
        detected = '失敗'
        senzai = 'なし'
        henkei = 'なし'
        sim = 0
        
        #print('=====================================================================================')
        #print()

        #print('駄洒落文：' + test)
        #print()

        kata = mecab_list(test)
            
        for x in range(len(kata)):
            try:
                #カタカナ変換
                kata2 = kata[x][4]

                #ひらがな変換
                kana = convert_kata_to_hira(kata2)

                url = "http://www.google.com/transliterate?"
                param = {'langpair':'ja-Hira|ja','text':kana}
                paramStr = urllib.parse.urlencode(param)
                ##print(url + paramStr)
                readObj = urllib.request.urlopen(url + paramStr)
                response = readObj.read()
                data = json.loads(response)
                fixed_data = json.loads(json.dumps(data[0], ensure_ascii=False))
                re_k = re.compile(r'(?:[々〇〻\u3400-\u9FFF\uF900-\uFAFF]|[\uD840-\uD87F]|[\uDC00-\uDFFF])+')

                for y in range(len(kata)):
                    for z in range(len(fixed_data[1])):
                        try:
                            #かな漢字変換後の単語と, その変換元の単語同士を計算しないように設定
                            if x != y:
                                doc_x = nlp(kata[y][0])
                                doc_x2 = doc_x[0]
                                doc_y = nlp(fixed_data[1][z])
                                doc_y2 = doc_y[0]
                                noun_toks = []

                                if re_k.match(fixed_data[1][z]):

                                    #普通名詞, 固有名詞, 動詞に限定
                                    if doc_x2.pos_ in ('NOUN', 'PROPN', 'VERB') and doc_y2.pos_ in ('NOUN', 'PROPN', 'VERB'):
                                        if kata[x][0] != fixed_data[1][z]:

                                            #コサイン類似度を計算
                                            cos = float(model.similarity(kata[y][0], fixed_data[1][z]))

                                            #コサイン類似度が0.4以上であれば潜在表現として検出
                                            if cos > 0.4:
                                                
                                                #print(kata[x][0]+'の漢字変換候補：' , fixed_data[1])
                                                #print()
                                                #print(kata[x][0]+' ===> '+ fixed_data[1][z] + ' に変換')
                                                # #print(lines2)
                                                #print(kata[y][0],'と', fixed_data[1][z],'のコサイン類似度：', cos)
                                                #print()
                                                #print('\033[32m'+'検出成功'+'\033[0m')
                                                #print()

                                                detected = '成功'
                                                senzai = fixed_data[1][z]
                                                henkei = kata[y][0]
                                                sim = cos

                                                return(detected, senzai, henkei, sim)
                        except:
                            pass
            except:
                pass
        return(detected, senzai, henkei, sim)
    

        
