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
from pprint import pprint
from string import digits
import spacy
from gensim.models import KeyedVectors

import requests
import json

#chiVeのモデル
model = gensim.models.KeyedVectors.load("./chive-1.2-mc5_gensim/chive-1.2-mc5.kv")

#ja_ginzaのロード
nlp = spacy.load('ja_ginza')

#分かち書き
wakati = MeCab.Tagger("-Owakati")


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


def chive(dajare):
  lines = dajare
  detected = '失敗'
  senzai = 'なし'
  henkei = 'なし'
  sim = 0
  
  #print('=====================================================================================')
  #print()
  #print('駄洒落文：' + dajare)
  word=format_text(dajare)
  #print(word)
  word2=wakati.parse(word).split()
  #print('分かち書き結果')
  #print(word2)
  #print()
  for x in range(len(word2)):
        try:
          #類似度が高い上位500件かつ値が0.4以上の単語を取得
          similar_words=model.most_similar(word2[x], topn=500)
          for y in range(len(similar_words)):
            if float(similar_words[y][1]) >= 0.4:
              text1=similar_words[y][0]
                #pprint(similar_words[y])

              #類似度が高い単語と駄洒落文中の単語の音韻類似度を計算  
              for z in range(len(word2)):
                text2=word2[z]

                #類似度が高い単語と, その取得元の単語同士を計算しないように設定 
                if x != z :
                  try:
                  #音韻類似度が0.5以上であれば検出成功
                    if similarity.similarity(text1,text2) > 0.5 :
                      
                      #普通名詞, 固有名詞, 動詞に限定
                      doc=nlp(word2[x])
                      for tok in doc:
                        if tok.pos_ in ('NOUN', 'PROPN', 'VERB'):
                          doc2=nlp(text1)
                          for tok2 in doc2:
                            if tok2.pos_ in ('NOUN', 'PROPN', 'VERB'):

                              lines = dajare
                              detected = '成功'
                              senzai = text1
                              henkei = word2[x]
                              sim = similar_words[y][1]
                          
                              print('"'+senzai+'"'+' と類似度が高い単語')
                              print(similar_words[y])
                              print()
                              print('"' + henkei + '" と駄洒落文中の "' + text2 + '" の音韻類似度:' , similarity.similarity(text1,text2))
                              print()
                              print('\033[32m'+ detected +'\033[0m')
                              print()
                              return(detected, senzai, henkei, sim, lines)
                  except:
                    pass
        except:
          pass
  return(detected, senzai, henkei, sim, lines)
# chive()