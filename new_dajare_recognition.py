#併置型
from operator import contains
import re
import spacy
from spacy.tokens import Doc
import MeCab
import ginza
import csv
from styleframe import StyleFrame
from pykakasi import kakasi
import sys
import pandas as pd
import jaconv
import itertools
import editdistance as ed
import Levenshtein as ls


class EditDistanceUtil():
  def __init__(self):
    self.re_mora = self.__get_mora_unit_re()

  #モウラ単位に分割するための正規表現パターンを得る
  def __get_mora_unit_re(self):
    #各条件を正規表現で表す
    c1 = '[ウクスツヌフムユルグズヅブプヴ][ヮァィェォ]' #ウ段＋「ヮ/ァ/ィ/ェ/ォ」
    c2 = '[イキシシニヒミリギジヂビピ][ャュェョ]' #イ段（「イ」を除く）＋「ャ/ュ/ェ/ョ」
    c3 = '[テデ][ャィュョ]' #「テ/デ」＋「ャ/ィ/ュ/ョ」
    c4 = '[ァ-ヴー]' #カタカナ１文字（長音含む）

    cond = '('+c1+'|'+c2+'|'+c3+'|'+c4+')'
    re_mora = re.compile(cond)
    return re_mora

  #カタカナ文字列をモウラ単位に分割したリストを返す
  def mora_wakachi(self, kana_text):
    return self.re_mora.findall(kana_text)

  def char2vowel(self, text):
    t = text[-1] #母音に変換するには最後の１文字を見れば良い
    if t in "アカサタナハマヤラワガザダバパァャヮ":
      return "ア"
    elif t in "イキシチニヒミリギジヂビピィ":
      return "イ"
    elif t in "ウクスツヌフムユルグズヅブプゥュヴ":
      return "ウ"
    elif t in "エケセテネヘメレゲゼデベペェ":
      return "エ"
    elif t in "オコソトノホモヨロヲゴゾドボポォョ":
      return "オ"
    elif t == "ン":
      return "ン"
    elif t == "ッ":
      return "ッ"
    else:
      print(text, "no match")
      return text

    #モーラリストを母音のリストに変換
  def vowel(self, text):
    t = text[-1] #母音に変換するには最後の１文字を見れば良い
    if t in "a":
      return "a"
    elif t in "k" + "," + "a":
      return "a"
    elif t == "N":
      return "NNNNNN"
    elif t == "ッ":
      return "ッ"
    else:
      print(text, "no matchggggggggggggg")
      return text

  #長音を母音に変換
  #入力はモウラの単位で分割されたカナのリスト
  def bar2vowel(self, kana_list):
    output = []
    output.append(kana_list[0])
    #最初に長音がくることは想定しないので、２番めの要素からループを始める
    for i,v in enumerate(kana_list[1:]):
      if v == "ー":
        #kana = self.char2vowel(output[i])#長音が連続した場合に対応するために念の為、outputから直前の要素を取得する
        kana = self.vowel(output[i])
      else:
        kana = v
      output.append(kana)
    return output

  #カナを母音に変換する
  def kana2vowel(self, kana_list):
    output = []
    for v in kana_list:
      #kana = self.char2vowel(v)
      kana = self.vowel(v)
      output.append(kana)
    return output

  #カナを母音に変換する
  def kana2vowel2(self, kana_list):
    output = []
    for v in kana_list:
      kana = self.char2vowel(v)
      output.append(kana)
    return output

  #受け取ったカナ１単位をアルファベットに変換して返す
  #入力はモウラ１単位に相当するカナ文字列（長さ１または２）
  def char2consonant(self, text):
    t = text[0] #アルファベットに変換するには最初の１文字を見れば良い
    if t in "ア":
      return "a"
    elif t in "イ":
      return "i"
    elif t in "ウ":
      return "u"
    elif t in "エ":
      return "e"
    elif t in "オ":
      return "o"
    elif t in "ヤ":
      return "y"+","+"a"
    elif t in "ユ":
      return "y"+","+"u"
    elif t in "ヨ":
      return "y"+","+"o"
    elif t in "ワ":
      return "w"+","+"a"
    elif t in "ヲ":
      return "w"+","+"o"
    elif t in "カ":
      return "k"+","+"a"
    elif t in "キ":
      return "k"+","+"i"
    elif t in "ク":
      return "k"+","+"u"
    elif t in "ケ":
      return "k"+","+"e"
    elif t in "コ":
      return "k"+","+"o"
    elif t in "サ":
      return "s"+","+"a"
    elif t in "シ":
      return "s"+","+"i"
    elif t in "ス":
      return "s"+","+"u"
    elif t in "セ":
      return "s"+","+"e"
    elif t in "ソ":
      return "s"+","+"o"
    elif t in "タ":
      return "t"+","+"a"
    elif t in "チ":
      return "t"+","+"i"
    elif t in "ツ":
      return "t"+","+"u"
    elif t in "テ":
      return "t"+","+"e"
    elif t in "ト":
      return "t"+","+"o"
    elif t in "ナ":
      return "n"+","+"a"
    elif t in "ニ":
      return "n"+","+"i"
    elif t in "ヌ":
      return "n"+","+"u"
    elif t in "ネ":
      return "n"+","+"e"
    elif t in "ノ":
      return "n"+","+"o"
    elif t in "ハ":
      return "h"+","+"a"
    elif t in "ヒ":
      return "h"+","+"i"
    elif t in "フ":
      return "h"+","+"u"
    elif t in "ヘ":
      return "h"+","+"e"
    elif t in "ㇹ":
      return "h"+","+"o"
    elif t in "マ":
      return "m"+","+"a"
    elif t in "ミ":
      return "m"+","+"i"
    elif t in "ム":
      return "m"+","+"u"
    elif t in "メ":
      return "m"+","+"e"
    elif t in "モ":
      return "m"+","+"o"
    elif t in "ラ":
      return "r"+","+"a"
    elif t in "リ":
      return "r"+","+"i"
    elif t in "ル":
      return "r"+","+"u"
    elif t in "レ":
      return "r"+","+"e"
    elif t in "ロ":
      return "r"+","+"o"
    elif t in "ガ":
      return "g"+","+"a"
    elif t in "ギ":
      return "g"+","+"i"
    elif t in "グ":
      return "g"+","+"u"
    elif t in "ゲ":
      return "g"+","+"e"
    elif t in "ゴ":
      return "g"+","+"o"
    elif t in "ザ":
      return "z"+","+"a"
    elif t in "ジ":
      return "z"+","+"i"
    elif t in "ズ":
      return "z"+","+"u"
    elif t in "ゼ":
      return "z"+","+"e"
    elif t in "ゾ":
      return "z"+","+"o"
    elif t in "ヂ":
      return "z"+","+"i"
    elif t in "ヅ":
      return "z"+","+"u"
    elif t in "ダ":
      return "d"+","+"a"
    elif t in "デ":
      return "d"+","+"e"
    elif t in "ド":
      return "d"+","+"o"
    elif t in "バ":
      return "b"+","+"a"
    elif t in "ビ":
      return "b"+","+"i"
    elif t in "ブ":
      return "b"+","+"u"
    elif t in "ベ":
      return "b"+","+"e"
    elif t in "ボ":
      return "b"+","+"o"
    elif t in "ヴ":
      return "b"+","+"u"
    elif t in "パ":
      return "p"+","+"a"
    elif t in "ピ":
      return "p"+","+"i"
    elif t in "プ":
      return "p"+","+"u"
    elif t in "ぺ":
      return "p"+","+"e"
    elif t in "ポ":
      return "p"+","+"o"
    elif t in "ョ":
      return "y"+","+"o"
    elif t in "ャ":
      return "y"+","+"a"
    elif t in "ュ":
      return "y"+","+"u"
    elif t == "ッ":
      return "q"
    elif t == "ン":
      return "N"
    elif t == "ー":
      return "-"
    else:
      print(text, "")
      return text
  #カナ文字列を子音にして返す
  def kana2consonant(self, kana_list):
    output = []
    for v in kana_list:
      kana = self.char2consonant(v)
      output.append(kana)
    return output

  
#一文の入力に対して併置型駄洒落の判定を行う
#if __name__=="__main__": #from spacy.language import Language まで
    #nlpオブジェクトを作成
nlp = spacy.load('ja_ginza_electra')
tagger = MeCab.Tagger("")
wakati = MeCab.Tagger("-Owakati")
m = MeCab.Tagger("-d /var/lib/mecab/dic/ipadic-utf8 -Ochasen")
yomi = MeCab.Tagger("-d /var/lib/mecab/dic/ipadic-utf8 -Oyomi")#カタカナに変換
edu = EditDistanceUtil()
w = csv.writer(sys.stdout, lineterminator="\n")
  
    #s1は入力文全体の母音のリスト、s2は種表現候補のトークンのモーラ列からの母音のリスト
def contains(s1, s2):
    count = 0
    for i, _ in enumerate(s1[:-len(s2)+1]):  # 終了位置に+1を付けた
        if s1[i:i+len(s2)] == s2:
            if count == 1:
                return (i, i+len(s2))
            count += 1
    return None

    # グローバルなクラスをインポート
from spacy.tokens import Span

    # Docに拡張をセット
Doc.set_extension('dajare', default={})

    # カスタムコンポーネントの追加
from spacy.language import Language

@Language.component("Dajare")
def dajare(doc):
    #辞書型オブジェクト
    doc._.dajare = dict()

    doc._.dajare['text'] = text
    if type_tane == 1 and type_henkei == 1 and thres == "最適な音韻類似度":
        doc._.dajare['type'] = "併置型"
    else:
        doc._.dajare['type'] = "不明"
    doc._.dajare['tane_word'] = tane_word
    doc._.dajare['span_tane'] = span_tane
    doc._.dajare['mora_tane'] = mora_tane
    doc._.dajare['mora_tane_word'] = tane_res1
    doc._.dajare['henkei_word'] = henkei_word
    doc._.dajare['span_henkei'] = span_henkei
    doc._.dajare['mora_henkei'] = mora_henkei
    doc._.dajare['mora_henkei_word'] = mora_henkei_word
    
    #for k in doc._.dajare:
        #print('%s  -> %s' % (k, doc._.dajare[k]))

    return doc


# テキストの種表現、変形表現を取得
#この寺の檀家はダンカン
#この古典の問題はコテンパン
#text = "古典の問題にコテンパンにやられた"
def heich(text):
  #print(wakati.parse(text).split())
  kara = ""
  threshold = 0
  q_tane_henkei = 0
  type_tane = 0
  type_henkei = 0
  henkei_spe = 0
  henkei_spe = 0
  mora_num = 0
  detected = ''
  type = ""         #テキストが併置型駄洒落であるか否か
  span_tane = ""    #種表現となる/含んでいるspan
  span_henkei = ""  #変形表現となる/含んでいるspan
  mora_tane = ""    #種表現spanにおける種表現の音素上の範囲
  mora_henkei = ""  #変形表現spanにおける変形表現の音素上の範囲
  tane_word = ""
  henkei_word = ""
  mora_henkei_word = ""
  tane_start_index = 0 #追加
  #print("入力:",text)          
  doc = nlp(text)
  #token.is_punct = Trueのトークンを削除（'、'や'？'など）
  punct_non_text = ""
  for token in doc:
      if   token.is_punct == False:
          punct_non_text = punct_non_text + token.text
      #else:
          #print("")
  text = punct_non_text

  moras1 = yomi.parse(text) #moras:カタカナ文字列
  text_mora = edu.kana2consonant(moras1)
  text_mora.remove('\n')
  print("不要な語摘出後の入力:",text)
  print("カタカナに変換",moras1)
  print("アルファベットに変換",text_mora)
  doc = nlp(text)

  #----------種リストの取得-------------
  t_list = []
  for token in doc:
      if token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]:
          t_list.append(token.text)

  tane_lst = []
  for tane in t_list:
      t_tane1 = edu.kana2consonant(yomi.parse(tane))
      t_tane1.remove("\n")
      tane_lst.append(t_tane1)

  mora_lst = []
  for token in doc: #形態素解析
      lst1 = edu.kana2consonant(yomi.parse(token.text))
      lst1.remove('\n')
      mora_lst.append(lst1)
  print("形態素ごとのモーラリスト:",mora_lst) #種表現候補の形態素のリスト

  q_count = 0
  lst1 = edu.kana2consonant(moras1)
  lst1.remove('\n')
  if 'q' in lst1:
      lst1 = [i for i in lst1 if i not in "q"] #すべてのq削除

  print("s1(入力文全体のモーラリスト)を出力:",mora_lst )

  # 種表現を探索
  t_lst1 = []
  tt_lst = []
  ri = list(itertools.chain.from_iterable(mora_lst))#一次元配列にする
  for tane in tane_lst:
      s1_str = "/".join(ri)
      tane_str = "/".join(tane)
      if s1_str.count(tane_str) >= 2: #s1の形態素の中で2回以上出現する形態素を出力
          t_lst1.append(tane)
          print("s1の形態素の中で2回以上出現するモーラ列：", tane)
      tane2 = "".join(tane) #taneを文字列に
      if tane2 in "".join(tane):  #2回以上出現するtaneを含む形態素を出力
          tt_lst.append(tane)
  print("s1の形態素の中で2回以上出現するモーラ列s2 ：",tt_lst)

  tane_res1 = ""
  max = 0
  if len(t_lst1) == 0 and len(tt_lst) == 0:  
      tt_lst = mora_lst[0]
  tane_res1 = tt_lst[0]
  print("s3(種表現候補のトークン)を出力:",tane_res1) 
  tane_list = []
  tane = 0

  #入力文と種表現の母音リスト、子音リストの取得
  s1_cons = []
  s1_vowel = []
  s2_cons = []
  s2_vowel = []
  for r in ri:
      s1_cons.append(r[0])
      s1_vowel.append(r[2:])
  for t in tane_res1:
      s2_cons.append(t[0])
      s2_vowel.append(t[2:])
  henkei_tuple = contains(s1_vowel,s2_vowel)

  #音韻類似度計算
  max_simi = 0
  ruizi_word = ""
  ruizi_list = []
  ev_list= []
  ev_list2= []
  for t in mora_lst:
      jaro = ls.jaro_winkler(t,tane_res1) #ジャロ・ウィンクラー距離
      if jaro == 1: 
          ruizi_list.append(t)
          if len(ruizi_list) >= 2:  #種表現と同じ形態素が２つ以上あったら
              ruizi_word = ruizi_list[-1:]  #後ろの形態素を変形表現とする
              threshold = jaro
      if len(ruizi_list) < 2:
          if 0 < jaro and jaro < 1:
              if max_simi < jaro:
                  max_simi = jaro
                  ruizi_word = t
              threshold = jaro
  print("ruizi_word",ruizi_word)

  #変形表現の閾値判定
  thres = "最適な音韻類似度"
  print("音韻類似度：",threshold)
  if threshold < 0.6:
      thres = "不適切な音韻類似度"
  #else:
      #print("")

  #[q]を消した場合
  s1_qcons = []
  s1_qvowel = []
  s2_qcons = []
  s2_qvowel = []
  #[q]がruizi_wordに含まれる場合
  if 'q' in ruizi_word: 
      q_count = 1
      for r in lst1:
          s1_qcons.append(r[0])
          s1_qvowel.append(r[2:])
      for t in tane_res1:
          s2_qcons.append(t[0])
          s2_qvowel.append(t[2:])
  henkei_qtuple = contains(s1_qvowel,s2_qvowel)
  print("henkei_qtuple",henkei_qtuple)

  #もしruizi_wordが見つからない場合のモーラ単位での変形表現取得
  if ruizi_word == "":
      for t in mora_lst:
          ev = ed.eval(t,tane_res1) #ev==0 は同じ語となる（類似している語は１か２）
          if ev == 1:
              ev_list.append(t)
              if len(ev_list) >= 2:
                  ruizi_word = ev_list[-1:]
              ruizi_word = t
              threshold = ev
          elif ev == 2:
              ev_list2.append(t)
              if len(ev_list2) >= 2:
                  ruizi_word = ev_list2[-1:]
              ruizi_word = t
              threshold = ev
      print("ruizi_word",ruizi_word)
  #変形表現の閾値判定
  thres = "最適な音韻類似度"
  print("音韻類似度：",threshold)
  if threshold < 0.6:
      thres = "不適切な音韻類似度"
  #else:
      #print("")

  #tane_res1とruizi_wordどちらにも「q」がある場合
  if "q" in tane_res1 and "q" in ruizi_word:
      q_tane_henkei = 1

  #種表現の再探索
  if henkei_tuple == "" or thres == "不適切な音韻類似度":
      for tane in tane_lst:
          s1_str = "/".join(ri)
          tane_str = "/".join(tane)
          if s1_str.count(tane_str) >= 2: #s1の形態素の中で2回以上出現する形態素を出力
              t_lst1.append(tane)
              print("s1の形態素の中で2回以上出現するモーラ列：  b", tane)
  # 種表現候補の中で最も文字数が多い形態素を出力
      for t in t_lst1:
          if max < len(t):
              max = len(t)
              tane_res1 = t
      print("s3(種表現候補のトークン)を再出力:",tane_res1 )
      #入力文と種表現の母音リスト、子音リストの取得
      s1_cons = []
      s1_vowel = []
      s2_cons = []
      s2_vowel = []
      for r in ri:
          s1_cons.append(r[0])
          s1_vowel.append(r[2:])
      for t in tane_res1:
          s2_cons.append(t[0])
          s2_vowel.append(t[2:])
      henkei_tuple = contains(s1_vowel,s2_vowel)
      print("henkei_tuple",henkei_tuple)
      #音韻類似度計算によるモーラ単位アライメント（変形表現の取得）
      max_simi = 0
      ruizi_word = ""
      ruizi_list = []
      ev_list= []
      ev_list2= []
      for t in mora_lst:
          jaro = ls.jaro_winkler(t,tane_res1) #ジャロ・ウィンクラー距離
          if jaro == 1: 
              ruizi_list.append(t)
              if len(ruizi_list) >= 2:  #種表現と同じ形態素が２つ以上あったら
                  ruizi_word = ruizi_list[-1:]  #後ろの形態素を変形表現とする
                  threshold = jaro
          if len(ruizi_list) < 2:
              if 0 < jaro and jaro < 1:
                  if max_simi < jaro:
                      max_simi = jaro
                      ruizi_word = t
                      threshold = jaro
      print("ruizi_word",ruizi_word)
      #変形表現の閾値判定
      thres = "最適な音韻類似度"
      print("音韻類似度：",threshold)
      if threshold < 0.6:
          thres = "不適切な音韻類似度"
      #else:
          #print("")

  #種表現の日本語取得
  for token in doc:
      t = edu.kana2consonant(yomi.parse(token.text))
      t.remove('\n')
      #span_tane,mora_taneの取得
      if tane_res1 == t:
          tane = 1
          if tane == 1:
              tane_word = token.text
              print("日本語の種表現",tane_word)
              tane_start_index = text.find(tane_word)       #種表現開始インデックス
              tane_end_index = tane_start_index + len(tane_word)  #種表現終了インデックス
              print(tane_end_index)
              tane_start_index = str(tane_start_index)
              tane_end_index = str(tane_end_index)
              span_tane = "(" + tane_start_index + "," + tane_end_index + ")"
              print("span_tane:",span_tane)

              mora_tane_start_index = mora_lst.index(tane_res1)   #モーラでの種表現開始インデックス
              if mora_tane_start_index != 0:
                  mora_tane_start_index = mora_tane_start_index + 2
              mora_tane_end_index = mora_tane_start_index + len(tane_res1)    #モーラでの種表現終了インデックス
              mora_tane_start_index = str(mora_tane_start_index)
              mora_tane_end_index = str(mora_tane_end_index)
              mora_tane = "(" + mora_tane_start_index + "," + mora_tane_end_index + ")"
              print("mora_tane:",mora_tane)
              if len(ri) <= int(mora_tane_start_index):
                  mora_tane_start_index = int(mora_tane_start_index) - 1
              if ri[int(mora_tane_start_index)] != tane_res1[0]:
                  mora_tane_start_index = int(mora_tane_start_index) - 1
                  mora_tane_end_index = int(mora_tane_end_index) - 1
                  mora_tane = "(" + str(mora_tane_start_index) + "," + str(mora_tane_end_index) + ")"
                  #if ri[int(mora_tane_start_index)] == tane_res1[0]:
                      #print
              print("mora_tane:",mora_tane)
              break;
      else:
          tane = 0

  print("tane_res1",tane_res1) #追加
  print("len(tane_res1)",len(tane_res1))　#追加len(tane_res1)
  # 種表現候補が分からない場合
  if len(tane_res1) == 0 or len(tane_res1) == 1: 
      lst = []
      
      # ハイフン削除
      l1 = [i for i in lst1 if i not in "-"] #すべての-削除
      lst.append(l1)

      # ハイフンを母音に変更
      l2 = ["u" if l == "-" else l for l in lst1]
      lst.append(l2)

      #mora_henkei_end_index=  0 #追加
      #mora_henkei_start_index = 0　#追加

  # 種表現候補が分かった場合
  else:     
      x1 = contains(ri, tane_res1)
      print("モーラ単位での種表現:", tane_res1)
      #もしx1(変形表現のタプル)が見つからない場合
      if x1 == None:
      #ruizi_wordをもとに日本語の変形表現を取得
          for token in doc:
              ru = edu.kana2consonant(yomi.parse(token.text))
              ru.remove('\n')
              while tane_res1 != ruizi_word:
                  if ruizi_word == ru:
                      ruizi_hensuu = 1
                      if ruizi_hensuu == 1:
                          henkei_word = token.text
                          henkei = 1
                          break;
                      break;
                  else:
                      break;
          print("日本語の変形表現を出力:",henkei_word)
          #span_henkeiの取得
          span_num = 0
          try:
              henkei_start_index = text.rfind(henkei_word)  #変形表現開始インデックス
          except:
              span_henkei = "None"
              henkei_start_index = 0
              henkei_end_index = 0
              span_num = 1
              print("span_henkei:", span_henkei)
          henkei_end_index = henkei_start_index + len(henkei_word)  #変形表現終了インデックス
          henkei_start_index = str(henkei_start_index)
          henkei_end_index = str(henkei_end_index)
          span_henkei = "(" + henkei_start_index + "," + henkei_end_index + ")"
          if span_num == 1:
              span_henkei = "None"
          print("span_henkei:",span_henkei)
          str_text = len(text)
          str_moras = len(moras1)
          #変形表現の開始位置、種表現の開始位置が同じ時
          #種表現、変形表現が同じ語の時
          if henkei_start_index == tane_start_index:
              henkei_start_index = text.find(henkei_word, len(tane_word)) #変形表現開始インデックス修正
              henkei_end_index = henkei_start_index + len(henkei_word)  #変形表現終了インデックス修正
              henkei_start_index = str(henkei_start_index)
              henkei_end_index = str(henkei_end_index)
              span_henkei = "(" + henkei_start_index + "," + henkei_end_index + ")"
              print("span_henkei修正後:",span_henkei)
          #まだ同じとき
          if henkei_start_index == tane_start_index:
              kana_henkei_word = yomi.parse(henkei_word)
              m_henkei_word = edu.kana2consonant(kana_henkei_word)
              m_henkei_word.remove('\n')
              m_henkei_word="".join(m_henkei_word)#リストを文字列に
              henkei_start_index = moras1.find(kana_henkei_word)#変形表現開始インデックス修正
              print("henkei_start",henkei_start_index)
              henkei_end_index = henkei_start_index + len(henkei_word)#変形表現終了インデックス修正
              span_henkei = "(" + str(henkei_start_index) + "," + str(henkei_end_index) + ")"
              print("span_henkei更に修正後:",span_henkei)

          #モーラ単位での変形表現タプル取得
          #henkei_tupleがない場合

          if henkei_tuple == None:
              try:
                  mora_henkei_start_index = [i for i, x in enumerate(ri) if x == ruizi_word[0]] #ruizi_wordの最初の文字を出力
                  mora_henkei_start_index = mora_henkei_start_index[1]
              except:
                  mora_henkei = "None"
                  mora_henkei_start_index = 0
                  mora_henkei_end_index = 0
                  mora_num = 1
              mora_henkei_end_index = int(mora_henkei_start_index) + len(ruizi_word)
              mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")" 
              if mora_num == 1:
                  mora_henkei = "None"
              print("mora_henkei",mora_henkei)

          #henkei_tupleがある場合
          else:
          #[q]消してない場合
              if q_count == 0 and q_tane_henkei == 1:
                  print("henkei_tuple",henkei_tuple) 
                  mora_henkei_end_index = henkei_tuple[1]  
                  mora_henkei_end_index = str(mora_henkei_end_index)
                  mora_henkei_start_index = str(henkei_tuple[0])
                  mora_henkei = "(" + mora_henkei_start_index + "," + mora_henkei_end_index + ")"
                  if ruizi_word == "":
                      ruizi_num = 1
                      if ruizi_num == 1:
                          mora_henkei = "None"
                  else:
                      if ri[henkei_tuple[0]] != ruizi_word[0]:  #mora_henkeiの位置修正
                        mora_henkei_start_index = int(henkei_tuple[0])
                        mora_henkei_end_index = int(henkei_tuple[1])
                        mora_henkei_start_index = mora_henkei_start_index - 1   #１つ前にする
                        mora_henkei_end_index = mora_henkei_end_index - 1
                        mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
                        if ri[mora_henkei_start_index] != ruizi_word[0]:
                          mora_henkei_start_index = int(mora_henkei_start_index)
                          mora_henkei_end_index = int(mora_henkei_end_index)
                          mora_henkei_start_index = mora_henkei_start_index + 2
                          mora_henkei_end_index = mora_henkei_end_index + 2
                          mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
              #[q]消した場合
              else: 
                  print("henkei_qtuple",henkei_qtuple)
                  if henkei_qtuple == None:
                    henkei_qtuple = henkei_tuple
                  mora_henkei_end_index = henkei_qtuple[1] + 1  #[q]を消した分、１つ増やす
                  mora_henkei_end_index = str(mora_henkei_end_index)
                  mora_henkei_start_index = str(henkei_qtuple[0])
                  mora_henkei = "(" + mora_henkei_start_index + "," + mora_henkei_end_index + ")"
              print("mora_henkeiaaa:",mora_henkei)
              #モーラ変形インデックスが正しく取れてるか判定
              mora_henkei_start_index = int(mora_henkei_start_index)
              mora_henkei_end_index = int(mora_henkei_end_index)
              mora_henkei_check = mora_henkei_end_index - mora_henkei_start_index
              print("mora_henkei_check:",mora_henkei_check)
              #修正
              if mora_henkei_check > len(henkei_word):
                  mora_henkei_end_index = mora_henkei_end_index - 1
                  mora_henkei_start_index = str(mora_henkei_start_index)
                  mora_henkei_end_index = str(mora_henkei_end_index)
                  mora_henkei = "(" + mora_henkei_start_index + "," + mora_henkei_end_index + ")"
                  print("mora_henkei修正:",mora_henkei)
              #elif mora_henkei_check == len(ruizi_word):
                  #print("同じ")
              #ruizi_wordがとれていない場合
              if ruizi_word == "" or len(ruizi_word) == 1:
                  pass
              else:
                  if ri[int(mora_henkei_start_index)] == ruizi_word[0]: #start_indexが正しいため、end_indexも正しくする
                      mora_henkei_end_index = int(mora_henkei_start_index) + len(ruizi_word) + 1
                      mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
                  else:
                      mora_henkei_start_index = int(mora_henkei_start_index) - 1
                      if ri[int(mora_henkei_start_index)] == ruizi_word[0]: #start_indexが正しいため、end_indexも正しくする
                          mora_henkei_end_index = int(mora_henkei_start_index) + len(ruizi_word) + 1
                          mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
                          if mora_henkei_end_index > len(ri):
                              mora_henkei_end_index = int(mora_henkei_end_index) - 1
                
          #不要な文字削除
          tane_word = re.sub("\<.+", "", tane_word)
          #data["tane extraction"][i] = tane_word
          henkei_word = henkei_word.replace('\n','')
          henkei_word = re.sub("\<.+", "", henkei_word)
          if henkei_word == "":
              henkei_word = "None"
          #data["henkei extraction"][i] = henkei_word
          print("henkei_word;:",henkei_word)
          #適切な併置型駄洒落かの処理
          if thres == "最適な音韻類似度":
              type_tane = 1
              type_henkei = 1
          elif henkei_word == "None":
              type_henkei = 0
          if henkei_word not in text:
              henkei_word = jaconv.hira2kata(henkei_word) #ひらがなをカタカナに変換
              if henkei_word not in text:
                  henkei_word = jaconv.kata2hira(henkei_word) #カタカナをひらがなに変換
                  print("henkei_word",henkei_word)
              else:
                  print("henkei_word;:",henkei_word)
          else:
              print("henkei_word;:",henkei_word)

      # 通常取り出せている場合 
      else:
          num1 = x1[0]
          if q_count == 1:
              num2 = x1[1] + 1
          else:
              num2 = x1[1]
          henkei_mozi = lst1[x1[0]:x1[1]]
          #x1番目のs1リストをx1番目の後の数字のモーラまで連結
          #henkei_listを取得
          print("x1,x2:",num1,num2)                         
          henkei_list = []
          c = 0             
          for t in mora_lst:
              while num1 < num2:
                  try:
                      henkei_list.append(ri[num1])                 
                      num1 = num1 + 1
                      if num1 == num2 + 1:                   
                          print("henkei_list",henkei_list)                   
                      else:                     
                          print("henkei_list",henkei_list)                      
                  except:
                  ##print("IndexError")
                      break;
          print("henkei_list",henkei_list)
          henkei = 0
          error = 0
          #モーラ単位の変形表現が1文字の場合うまく取れてないため、henkei_listに変える
          if len(ruizi_word) == 1:
              ruizi_word = henkei_list
          #形態素解析し、henkei_listと一致する形態素を取得し、日本語で変形表現として出力
          for token in doc:
              lst1 = edu.kana2consonant(yomi.parse(token.text))
              lst1.remove('\n')
              #モーラ単位の形態素と音韻類似している変形表現候補と一致しているか
              #変形表現探索
              while tane_res1 != ruizi_word:
                  if ruizi_word == lst1:
                      print("変形表現の形態素を出力",ruizi_word)               
                      henkei = 1
                      if henkei == 1:
                          henkei_word = token.text
                          print("日本語の変形表現:",henkei_word)
                          break;
                      break;
                  else:
                      break;
              if lst1 == ruizi_word:
                  print("変形表現の形態素を出力",ruizi_word)
                  henkei = 1
                  if henkei == 1:
                      henkei_word = token.text
              #else:
                  #print
          
          if henkei_word == tane_word:
              henkei = 0

          #もし変形表現をうまくとりだせず、完全一致の形態素を出力する場合
          if henkei == 0:
              henkei_spe = 1
              numero1 = x1[0]
              numero2 = x1[1] + 1
              numero3 = numero2 - numero1
              henkei_ja_index = ''
              while numero1 < numero2:
                  if len(moras1) < numero2 :
                      error = 1
                      numero1 = 1
                      numero2 = 3
                      break;
                  henkei_ja_index = henkei_ja_index + moras1[numero1]
                  numero1 += 1
                  if len(moras1) <= numero2:
                      numero2 = x1[1]                      
                  henkei_ja_index = henkei_ja_index + moras1[numero1]
                  numero1 += 1                                 
              h_words = jaconv.kata2hira(henkei_ja_index) #カタカナをひらがなに変換
              henkei_word = h_words
          #else:
              #print("正しい")
          
          #不要な文字削除
          tane_word = re.sub("\<.+", "", tane_word)
          henkei_word = henkei_word.replace('\n','')
          henkei_word = re.sub("\<.+", "", henkei_word)
          print("tane_word:",tane_word)
          s_henkei_word = henkei_word
          #適切な併置型駄洒落かの処理
          if thres == "最適な音韻類似度":
              type_tane = 1
              type_henkei = 1
          elif henkei_word == "None":
              type_henkei = 0
          if henkei_word not in text:
              henkei_word = jaconv.hira2kata(henkei_word) #ひらがなをカタカナに変換
              if henkei_word not in text:
                  henkei_word = jaconv.kata2hira(henkei_word) #カタカナをひらがなに変換
              else:
                  print("henkei_word;:",henkei_word)
          else:
              print("henkei_word;:",henkei_word)

          #span_taneの取得
          span_num = 0
          try:
              henkei_start_index = text.index(henkei_word)  #変形表現開始インデックス
          except:
              span_henkei = "None"
              henkei_start_index = 0
              henkei_end_index = 0
              span_num = 1
              print("span_henkei:", span_henkei)
          henkei_end_index = henkei_start_index + len(henkei_word)  #変形表現終了インデックス
          henkei_start_index = str(henkei_start_index)
          henkei_end_index = str(henkei_end_index)
          span_henkei = "(" + henkei_start_index + "," + henkei_end_index + ")"
          if span_num == 1:
              span_henkei = "None"
          print("span_henkei:",span_henkei)
          str_text = len(text)
          str_moras = len(moras1)
          #変形表現の開始位置、種表現の開始位置が同じ時
          #種表現、変形表現が同じ語の時
          if henkei_start_index == tane_start_index:
              henkei_start_index = text.find(henkei_word, len(tane_word)) #変形表現開始インデックス修正
              if henkei_start_index < 0:
                  henkei_start_index = int(henkei_start_index) + 1
              henkei_end_index = henkei_start_index + len(henkei_word)  #変形表現終了インデックス修正
              henkei_start_index = str(henkei_start_index)
              henkei_end_index = str(henkei_end_index)
              span_henkei = "(" + henkei_start_index + "," + henkei_end_index + ")"
              print("span_henkei修正後qq:",span_henkei)
          #まだ同じとき
          if henkei_start_index == tane_start_index:
              kana_henkei_word = yomi.parse(henkei_word)
              m_henkei_word = edu.kana2consonant(kana_henkei_word)
              m_henkei_word.remove('\n')
              m_henkei_word="".join(m_henkei_word)#リストを文字列に
              henkei_start_index = moras1.find(kana_henkei_word)#変形表現開始インデックス修正
              henkei_end_index = henkei_start_index + len(henkei_word)#変形表現終了インデックス修正
              span_henkei = "(" + str(henkei_start_index) + "," + str(henkei_end_index) + ")"
              print("span_henkei更に修正後:",span_henkei)
          #モーラ単位での変形表現タプル取得
          if henkei_spe == 1:
              mora_henkei_end_index = x1[1] + 1
              mora_henkei_end_index = str(mora_henkei_end_index)
              mora_henkei_start_index = str(x1[0])
              mora_henkei = "(" + mora_henkei_start_index + "," + mora_henkei_end_index + ")"
              print("mora_henkei:",mora_henkei)
              #モーラ変形インデックスが正しく取れてるか判定
              mora_henkei_start_index = int(mora_henkei_start_index)
              mora_henkei_end_index = int(mora_henkei_end_index)
              mora_henkei_check = mora_henkei_end_index - mora_henkei_start_index
              if mora_henkei_check > len(henkei_word):
                  mora_henkei_end_index = mora_henkei_end_index - 1
                  mora_henkei_start_index = str(mora_henkei_start_index)
                  mora_henkei_end_index = str(mora_henkei_end_index)
                  mora_henkei = "(" + mora_henkei_start_index + "," + mora_henkei_end_index + ")"
                  print("mora_henkei修正:",mora_henkei)
              #elif mora_henkei_check == len(ruizi_word):
                  #print("同じ")
              if ruizi_word == "" or len(ruizi_word) == 1:
                  pass
              else:
                  if ri[int(mora_henkei_start_index)] == ruizi_word[0]: #start_indexが正しいため、end_indexも正しくする
                      mora_henkei_end_index = int(mora_henkei_start_index) + len(ruizi_word) + 1
                      mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
                  else:
                      mora_henkei_start_index = int(mora_henkei_start_index) - 1
                      if ri[int(mora_henkei_start_index)] == ruizi_word[0]: #start_indexが正しいため、end_indexも正しくする
                          mora_henkei_end_index = int(mora_henkei_start_index) + len(ruizi_word) + 1
                          mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
                          if mora_henkei_end_index > len(ri):
                              mora_henkei_end_index = int(mora_henkei_end_index) - 1
          else:
              mora_henkei_end_index = x1[1]
              mora_henkei_end_index = str(mora_henkei_end_index)
              mora_henkei_start_index = str(x1[0])
              mora_henkei = "(" + mora_henkei_start_index + "," + mora_henkei_end_index + ")"
              print("mora_henkei:",mora_henkei)
              #モーラ変形インデックスが正しく取れてるか判定
              mora_henkei_start_index = int(mora_henkei_start_index)
              mora_henkei_end_index = int(mora_henkei_end_index)
              mora_henkei_check = mora_henkei_end_index - mora_henkei_start_index
              if mora_henkei_check > len(henkei_word):
                      mora_henkei_end_index = mora_henkei_end_index - 1
                      mora_henkei_start_index = str(mora_henkei_start_index)
                      mora_henkei_end_index = str(mora_henkei_end_index)
                      mora_henkei = "(" + mora_henkei_start_index + "," + mora_henkei_end_index + ")"
                      print("mora_henkei修正:",mora_henkei)
              #elif mora_henkei_check == len(ruizi_word):
                  #print("同じ")
              if ri[int(mora_henkei_start_index)] == ruizi_word[0]: #start_indexが正しいため、end_indexも正しくする
                  mora_henkei_end_index = int(mora_henkei_start_index) + len(ruizi_word) + 1
                  mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
              else:
                  mora_henkei_start_index = int(mora_henkei_start_index) - 1
                  if ri[int(mora_henkei_start_index)] == ruizi_word[0]: #start_indexが正しいため、end_indexも正しくする
                      mora_henkei_end_index = int(mora_henkei_start_index) + len(ruizi_word) + 1
                      mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
                      if mora_henkei_end_index > len(ri):
                          mora_henkei_end_index = int(mora_henkei_end_index) - 1
              #ruizi_wordが見つからないまたは、1文字の時
              if ruizi_word == None or len(ruizi_word) == 1:
                  pass
              else:
                  if ri[int(mora_henkei_start_index)] == ruizi_word[0]: #start_indexが正しいため、end_indexも正しくする
                      mora_henkei_end_index = int(mora_henkei_start_index) + len(ruizi_word) + 1
                      mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
                  else:
                      mora_henkei_start_index = int(mora_henkei_start_index) - 1
                      if ri[int(mora_henkei_start_index)] == ruizi_word[0]: #start_indexが正しいため、end_indexも正しくする
                          mora_henkei_end_index = int(mora_henkei_start_index) + len(ruizi_word) + 1
                          mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"
                          if mora_henkei_end_index > len(ri):
                              mora_henkei_end_index = int(mora_henkei_end_index) - 1
  mora_henkei_check = int(mora_henkei_end_index) -int(mora_henkei_start_index)
  if len(henkei_word) != mora_henkei_check:
      mora_henkei_end_index = int(mora_henkei_end_index) - 1
  mora_henkei = "(" + str(mora_henkei_start_index) + "," + str(mora_henkei_end_index) + ")"

  if type_tane == 1 and type_henkei == 1 and thres == "最適な音韻類似度":
      #print("このテキストは併置型駄洒落である")
      type = "併置型"
      detected = '成功'
  else:
      #print("このテキストは駄洒落でない又は認識失敗")
      type = "不明"
      detected = '失敗'
  kana_henkei = yomi.parse(henkei_word)
  mora_henkei_word = edu.kana2consonant(kana_henkei)
  mora_henkei_word.remove('\n')
  print("種表現: " + tane_word + ", 変形表現:" + henkei_word + ", type:" + type + ", span_tane:" + span_tane + ", mora_tane:" + mora_tane + ", mora_tane_word:" + str(tane_res1) + ", span_henkei:" + span_henkei + ", mora_henkei:" + mora_henkei + ", mora_henkei_word:" + str(mora_henkei_word))
  return(detected, tane_word, henkei_word)

#パイプラインに追加
#nlp.add_pipe('Dajare')
#print("Pipeline",nlp.pipe_names)
#doc = nlp(text)
