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
      #print(text, "no match")
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
      #print(text, "no matchggggggggggggg")
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
    elif t in "ペ":
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
      #print(text, "")
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

#カタカナ→ひらがな
def convertKtoH(text):
  result = jaconv.kata2hira(text)
  return result

def flatten(input_list):
    result = []
    for item in input_list:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

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
  #print("不要な語摘出後の入力:",text)
  #print("カタカナに変換",moras1)
  text_hira=convertKtoH(moras1)
  #print("ひらがなに変換",text_hira)
  #print("アルファベットに変換",text_mora)

  text_lst =[]
  del_lst = []
  for i in range(len(text)):
    text_lst.append(text[i])
  for i in range(len(text_lst)):
    if text_lst[i] == '<' and i not in del_lst:
      del_lst.append(i)
      for j in range(i+1, len(text_lst),1):
        if text_lst[j] != '>' and text_lst[j] != '＞' and text_lst[j] != ')' and text_lst[j] !='）':
          del_lst.append(j)
        else:
          del_lst.append(j)
          break;
    if text_lst[i] == '＜' and i not in del_lst:
      del_lst.append(i)
      for j in range(i+1, len(text_lst),1):
        if text_lst[j] != '>' and text_lst[j] != '＞' and text_lst[j] != ')' and text_lst[j] !='）':
          del_lst.append(j)
        else:
          del_lst.append(j)
          break;
    if text_lst[i] == '(' and i not in del_lst:
      del_lst.append(i)
      for j in range(i+1, len(text_lst),1):
        if text_lst[j] != '>' and text_lst[j] != '＞' and text_lst[j] != ')' and text_lst[j] !='）':
          del_lst.append(j)
        else:
          del_lst.append(j)
          break;
    if text_lst[i] == '（' and i not in del_lst:
      del_lst.append(i)
      for j in range(i+1, len(text_lst),1):
        if text_lst[j] != '>' and text_lst[j] != '＞' and text_lst[j] != ')' and text_lst[j] !='）':
          del_lst.append(j)
        else:
          del_lst.append(j)
          break;
  if del_lst:
    print("del_lst:",del_lst)
    for i in sorted(del_lst, reverse=True):
      text_lst.pop(i)
  text = ''.join(text_lst)
  doc = nlp(text)

  #----------種リストの取得-------------
  t_list = []
  del_lst = []
  doc_index = 0
    
  for token in doc:
    if token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]:
      t_list.append(token.text)
  
  #空白削除
  while '\u3000' in t_list:
    t_list.remove('\u3000')
  print("t_list:",t_list)

  tane_lst = []
  for tane in t_list:
      t_tane1 = edu.kana2consonant(yomi.parse(tane))
      t_tane1.remove("\n")
      tane_lst.append(t_tane1)
  print("種表現候補tane_lst：",tane_lst) 

  mora_lst = []
  mora_jp_lst = []
  for token in doc: #形態素解析
      if '\u3000' not in token.text:
        mora_jp_lst.append(token.text)
        lst1 = edu.kana2consonant(yomi.parse(token.text))
        lst1.remove('\n')
        mora_lst.append(lst1)

  print("mora_jp_lst:",mora_jp_lst) #形態素日本語リスト
  print("形態素ごとのモーラリスト:",mora_lst) #形態素のリスト

  q_count = 0
  lst1 = edu.kana2consonant(moras1)
  lst1.remove('\n')
  if 'q' in lst1:
      lst1 = [i for i in lst1 if i not in "q"] #すべてのq削除

  #print("s1(入力文全体のモーラリスト)を出力:",mora_lst )

  
  #変形表現候補のリスト作成
  henkei_lst = [] #変形表現候補のリスト
  henkei_jp_lst = [] #変形表現候補の日本語リスト
  henkei_elements_used = [] #変形表現候補に形態素のどの要素が使われているか

  for i in range(len(mora_lst)):
      for j in range(i, len(mora_lst)):
          substring = mora_lst[i:j+1]  
          substring_jp = mora_jp_lst[i:j+1]
          elements_used = [str(k) for k in range(i, j+1)]
          henkei_lst.append(substring)
          henkei_jp_lst.append(substring_jp)
          henkei_elements_used.append(elements_used)

  #余計な[]を消す
  henkei_lst = [flatten(sublist) for sublist in henkei_lst]
  #print("henkei_lst:",henkei_lst)
  #print("henkei_jp_lst:",henkei_jp_lst)
  #print("henkei_elements_used:",henkei_elements_used)

  #tane_moraの偶数番目にtaneの番号、奇数番目にtaneと同じmoraの番号
  tane_mora=[]
  same_char=[]
  mora_flag=0
  tane_flag=0
  for t in tane_lst:
    mora_flag=0
    for m in mora_lst:
      jaro = ls.jaro_winkler(m,t)
      if jaro == 1:
        same_char.append(mora_flag)
      mora_flag = mora_flag + 1
    print("same_char:",same_char)
    if len(same_char) >= 2:
      for s in same_char:
        if s not in tane_mora[1::2]:
          tane_mora.append(tane_flag)
          tane_mora.append(s)
          break;
    elif len(same_char) == 1:
      tane_mora.append(tane_flag)
      tane_mora.append(same_char[0])
    tane_flag = tane_flag + 1
    same_char.clear()
  
  print("tane_mora:",tane_mora)

  #音韻類似度計算
  max_simi = 0
  ruizi_word = ""
  ruizi_list = []
  ev_list= []
  ev_list2= []
  tane_index = None
  henkei_index = None
  tane_flag = 0
  henkei_flag = 0
  tane_mora_flag = 0
  a = None
  tane_word_lst = []
  tane_index_lst = []
  henkei_word_lst = []
  henkei_index_lst = []
  threshold_lst = []
  for n in tane_lst:
    henkei_flag = 0
    for t in henkei_lst:
      tane_mora_flag = 0
      for i in tane_mora[0::2]:
        if tane_flag == i:
          a=tane_mora[tane_mora_flag+1] #taneと同じmoraの番号
          break;
        else:
          a=None
        tane_mora_flag = tane_mora_flag + 2
      if str(a) not in henkei_elements_used[henkei_flag]:
        if len(n) > 1: #種表現は2文字以上
          if len(n) == 2: #種表現が2文字の場合、変形表現は種表現と同じかそれ以上の文字数
            if len(t) >= len(n):
              jaro = ls.jaro_winkler(t,n) #ジャロ・ウィンクラー距離
              if 0.6 <= jaro and jaro <= 1: 
                tane_word_lst.append(n)
                henkei_word_lst.append(t)
                threshold_lst.append(jaro)
                tane_index_lst.append(tane_flag)
                henkei_index_lst.append(henkei_flag)
                print("種表現:",n,"変形表現:",t,"音韻類似度:",jaro)
                if max_simi < jaro:
                  max_simi = jaro
                  threshold = jaro
          if len(n) > 2 and len(n) <=4: #種表現が3文字以上4文字以下の場合、変形表現は種表現の文字数-1以上の文字数
            if len(t)>=len(n)-1:
              jaro = ls.jaro_winkler(t,n) #ジャロ・ウィンクラー距離
              if 0.6 <= jaro and jaro <= 1: 
                tane_word_lst.append(n)
                henkei_word_lst.append(t)
                threshold_lst.append(jaro)
                tane_index_lst.append(tane_flag)
                henkei_index_lst.append(henkei_flag)
                print("種表現:",n,"変形表現:",t,"音韻類似度:",jaro)
                if max_simi < jaro:
                  max_simi = jaro
                  threshold = jaro
          if len(n) > 4: #種表現が5文字以上の場合、変形表現は種表現の文字数-2以上の文字数
            if len(t)>=len(n)-2:
              jaro = ls.jaro_winkler(t,n) #ジャロ・ウィンクラー距離
              if 0.6 <= jaro and jaro <= 1: 
                tane_word_lst.append(n)
                henkei_word_lst.append(t)
                threshold_lst.append(jaro)
                tane_index_lst.append(tane_flag)
                henkei_index_lst.append(henkei_flag)
                print("種表現:",n,"変形表現:",t,"音韻類似度:",jaro)
                if max_simi < jaro:
                  max_simi = jaro
                  threshold = jaro
      henkei_flag = henkei_flag + 1
    tane_flag = tane_flag + 1
        

  #変形表現の閾値判定
  thres = "適切な音韻類似度"
  if threshold == 0:
    thres = "不適切な音韻類似度"

  #種表現リスト、変形表現リストの日本語取得
  henkeiL_word = []
  if tane_word_lst:
    for i in range(len(tane_word_lst)):
      tane_word_lst[i] = t_list[tane_index_lst[i]]

      henkeiL_word = str(henkei_jp_lst[henkei_index_lst[i]])
      henkeiL_word = henkeiL_word.replace("'","")
      henkeiL_word = henkeiL_word.replace("[","")
      henkeiL_word = henkeiL_word.replace("]","")
      henkeiL_word = henkeiL_word.replace(",","")
      henkeiL_word = henkeiL_word.replace(" ","")
      henkei_word_lst[i] = henkeiL_word
  print("種表現のリスト:",tane_word_lst) 
  print("変形表現のリスト:",henkei_word_lst) 

  #種表現と変形表現のの日本語取得
  max_simi = 0
  if tane_word_lst:
    for i in range(len(threshold_lst)):
      if max_simi < threshold_lst[i]:
        max_simi = threshold_lst[i]
        tane_word = tane_word_lst[i]
        henkei_word = henkei_word_lst[i]
    print("種表現：",tane_word)
    print("変形表現：",henkei_word)
  else:
    tane_word = "なし"
    henkei_word = "なし"
    print("種表現：",tane_word)
    print("変形表現：",henkei_word)
  #類似度の高い上位n位の種表現、変形表現、類似度
  rank_tane_lst = []
  rank_henkei_lst = []
  rank_thres_lst = []
  index = None

  if tane_word_lst:
    for i in range(20):
      if tane_word_lst:
        rank_thres_lst.append(max(threshold_lst))
        index = threshold_lst.index(max(threshold_lst))
        rank_tane_lst.append(tane_word_lst[index])
        rank_henkei_lst.append(henkei_word_lst[index])
        threshold_lst.pop(index)
        tane_word_lst.pop(index)
        henkei_word_lst.pop(index)
        print(i+1,"位　種表現:",rank_tane_lst[i],"変形表現:",rank_henkei_lst[i],"音韻類似度:",rank_thres_lst[i])
      else:
        break;

  if tane_word != "" and henkei_word != "" and thres == "適切な音韻類似度":
    type = "併置型"
    detected="成功"
  else:
    type = "不明"
    detected="失敗"

  return(detected, tane_word, henkei_word, rank_tane_lst, rank_henkei_lst, rank_thres_lst, type)

#パイプラインに追加
#nlp.add_pipe('Dajare')
#print("Pipeline",nlp.pipe_names)
#doc = nlp(text)
