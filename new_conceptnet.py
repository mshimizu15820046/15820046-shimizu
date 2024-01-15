#重畳型

import re
import sys
import codecs
import time
from enum import Enum

import requests
import spacy
import ginza
from icecream import ic
import Levenshtein as ls
import pykakasi

from similarity import *

nlp = spacy.load('ja_ginza')
#nlp = spacy.load('ja_ginza_electra')
ginza.set_split_mode(nlp, 'C') # 形態素解析：分割単位の設定 (形態素長さ: A < B < C)

URL_LIST = ['http://api.conceptnet.io']  # Knowledge graph URLs
#URL_LIST = ['http://133.2.207.190:8084']  # Local ConceptNet5 API

PARAM_LIMIT = ""  # 空のままにすること
LIMIT = "20"  # 20件がデフォルト

kks = pykakasi.kakasi()


class Place(Enum):
    """Enum定数．主語->目的語か主語<-目的語か"""
    SUBJ = 1
    OBJ = 2


class Candidate:
    """潜在表現（候補）のデータクラス"""
    def __init__(self,
                 subject: str = "",                  # トリプルの主語位置にあるリソース
                 object: str = "",                   # トリプルの目的語位置にあるリソース
                 relation: str = "",                 # トリプルの述語（関係）
                 org_res_label: str = "",            # 潜在表現候補抽出のために参照したリソースのラベル
                 depth: int = 0,                     # find_latent_expression 再帰関数実行時の再帰深さ
                 place: Place = Place.OBJ) -> None:  # subject, object のどちらの位置が潜在表現となるか
        self.subject = subject
        self.object = object
        self.org_res_label = org_res_label
        self.relation = relation
        self.depth = depth
        self.place = place


    def getLatentExp(self) -> str:
        """Placeに応じて潜在表現を返す"""
        if self.place == Place.SUBJ:  # [主語] --関係-> 目的語.   []は潜在表現
            return self.subject
        else:                         # 主語 --関係-> [目的語]
            return self.object

    def getLatentExpLabel(self) -> str:
        exp = self.getLatentExp()
        if len(exp) > 6:
            return self.getLatentExp()[6:]
        else:
            return ""

    def getContentWord(self) -> str:
        """Placeに応じて潜在表現の抽出元リソースであった内容語を返す"""
        if self.place == Place.SUBJ:  # 主語 --関係-> [目的語].    []は内容語
            return self.object
        else:                         # [主語] --関係-> 目的語
            return self.subject

    def getOrigContentWord(self) -> str:
        """再帰的処理の始めに指定された入力文中の目的語を返す"""
        return self.org_res_label

    def getDirectedRelation(self) -> str:
        """Placeに応じて，関係名とともに左(主語)または右(目的語)を指す矢印を返す"""
        return ("--('{}')->" if self.place == Place.OBJ else "<-('{}')--").format(self.relation)

    def __str__(self):
        """文字列へ変換（可視化）
        
        >>> c = Candidate("/c/ja/大分県", "/c/ja/九州", "PartOf", "大分県", 1, Place.OBJ)
        >>> c
        1| 大分県 => '/c/ja/大分県' --('RelatedTo')-> '/c/ja/九州' => /c/ja/九州
        """
        return "{}| {} => '{}' {} '{}' => {}".format(
            self.depth,
            self.getOrigContentWord(),
            self.getContentWord(),
            self.getDirectedRelation(),
            self.getLatentExp(),
            self.getLatentExp(),
        )

    def __repr__(self):
        """文字列へ変換（コード形式）--> 可視化に変更 (__str__()の結果のみ出力)
        
        >>> c
        "Candidate('/c/ja/大分県', '/c/ja/九州', '大分県', 1, Place.OBJ)"
        """
        #return f"Candidate('{self.subject}', '{self.object}', '{self.org_res_label}', {self.depth}, {self.place})"
        return self.__str__()

def getLastURI(uri_list):
        #URIの最後だけのリストを得る
        last_parts = [uri.split('/')[-1] for uri in uri_list]
        return last_parts


def find_content_word_morpheme_list(dajare):
    """入力文から内容語形態素のみを抽出しリストに格納したものを返す．
    内容語形態素とする品詞：名詞(NOUN)，代名詞(PRONOUN)，動詞(VERB)，形容詞(ADJ)，副詞(ADV)
    Params:
        input_text: input dajare text.
    """
    dajare = re.sub('','',dajare)
    doc = nlp(dajare)

    # # 辞書に含ませたくない単語のリスト
    STOP_WORDS = ['[', ']', '(', ')', '-', '/', '.', ',', '=','は','の','が','に','']
    POS  = ("名詞-普通名詞","動詞-一般","名詞-固有名詞","感動詞-一般","副詞-一般","形容詞-一般")

    #絞り結果を格納
    content_word_morpheme_list = []
    #絞り込み
    for sent in doc.sents:
        for token in sent:
            if any(token.tag_.startswith(posp) for posp in POS):
                if str(token) in STOP_WORDS:
                    continue
                #print(token.orth_, token.tag_)
                #token.tag_:形態素(原形)のみの行列
                content_word_morpheme_list.append(token)
        #print('EOS')
    #print("内容語形態素抽出:", content_word_morpheme_list)
    #print()
    return content_word_morpheme_list

def find_tane_henkei_list(dajare): #種表現候補と変形表現候補を抽出
    doc = nlp(dajare)
    punct_non_text = ""
    for token in doc:
        if token.is_punct == False:
            punct_non_text = punct_non_text + token.text
    word = punct_non_text
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
    t_lst = [] #種表現リスト
    tk_lst = [] #種表現カナリスト
    tk_elements_lst = [] 
    for token in doc:
        if not token.is_space:
            if token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]:
                t_lst.append(token)
                tk_lst.append(token.morph.get("Reading"))
                tk_elements_lst.append(token_flag)
            token_flag = token_flag + 1
    tk_number_lst = [] #種表現が入力文のどこにあるか
    for i in tk_elements_lst:
        tk_number_lst.append(yomi_number_lst[i])
    text = ""
    for i in yomi_lst:
        mora_text = str(i).replace("'","")
        mora_text = mora_text.replace("[","")
        mora_text = mora_text.replace("]","")
        text += mora_text
    
    henkei_lst = [] #変形表現リスト
    henkei_element_used = [] #変形表現が入力文のどこにあるか

    for i in range(len(text)):
        for j in range(i, len(text)):
            substring = text[i:j+1]
            henkei_lst.append(substring)
            elements_used = [k for k in range(i, j+1)]
            #print(elements_used)
            henkei_element_used.append(elements_used)
    
    #henkei_elements_usedから''を削除
    henkei_elements_used = [[int(element) for element in sub_list] for sub_list in henkei_element_used]

    #print("種表現リスト:",t_lst)
    #print("種表現カナリスト:",tk_lst)
    #print("種表現エレメントリスト:",tk_number_lst)
    #print("変形表現リスト:",henkei_lst)
    #print("変形表現エレメントリスト;",henkei_element_used)

    return(t_lst, tk_lst, tk_number_lst, henkei_lst, henkei_element_used)


def not_similar(string1, string2):
    """string1とstring2が同じ文字列でない，または，一方が他方に含まれない"""
    return string1 != string2


# content_word_morpheme_list = find_content_word_morpheme_list('この鮭の卵、いくら？ ')
def find_latent_expression_candidates(res,org_res_label,depth):
    """
    ConceptNet5のリソース res を起点とする部分グラフより，
    内容語形態素リストcwmlの内容語との関連語(潜在表現候補)を全て取得する．
    org_res_labelは潜在表現候補探索するための基点リソースのラベルであり、潜在表現候補を取得する際に再び同じ名前のリソースを候補にするのを防ぐために与える
    termは接頭辞付きのラベル　ex.)/r,/c/ja
    """

    latent_expression_cand_dict: dict[str, set[Candidate]] = {}  # 型を指定
    related_res_list = []

    resp = requests.get(res + PARAM_LIMIT)
    # time.sleep(0.5)  # 公式APIを利用する際に必要
    result = resp.json()
    searching_res_term = result["@id"]
    searching_res_label = searching_res_term[6:]
    if org_res_label == "":
        org_res_label = searching_res_label
    #ic(searching_res_term, org_res_label)


    # termは接頭辞 ("/r", "/c/ja" など) 付きのラベル
    for e in result["edges"]:
        subj_term = e["start"]["term"]
        subj_label = e["start"]["label"]
        obj_term = e["end"]["term"]
        obj_label = e["end"]["label"]
        rel = e["rel"]["label"]
        predicate = e["rel"]["label"]

        if searching_res_label not in latent_expression_cand_dict:
            latent_expression_cand_dict[org_res_label] = set()
            #ic(latent_expression_cand_dict)

        # 潜在表現候補の制約を満たし，かつ，潜在表現がタプル目的語である場合
        if all((searching_res_term == subj_term ,"/c/ja" in obj_term)): 
            cand = Candidate(subject=subj_term,
                             object=obj_term,
                             org_res_label=org_res_label,
                             relation=predicate,
                             depth=depth,
                             place=Place.OBJ)
            extracted_term = cand.object
        # 潜在表現候補の制約を満たし，かつ，潜在表現がタプル主語である場合
        elif all((searching_res_term == obj_term,"/c/ja" in subj_term)):
            cand = Candidate(subject=subj_term,
                             object=obj_term,
                             org_res_label=org_res_label,
                             relation=predicate,
                             depth=depth,
                             place=Place.SUBJ)
            extracted_term = cand.subject
        # 潜在表現候補の制約を満たさない場合
        else:
            ##print(f"候補不可| {res} => '{subj_term}' -('{rel}')-> '{obj_term}'")
            continue

        # 潜在表現候補オブジェクトを登録
        latent_expression_cand_dict[org_res_label].add(cand)
        related_res_list.append(URL_LIST[0]+extracted_term)

        #print("候補追加" + str(cand))
    
    return latent_expression_cand_dict, related_res_list



def detect_latent_expression(cwm, res_list): #音韻類似度計算
    detected_candidates = list()
    cwm_text = cwm


    #print("res_list:",res_list)
    related_resource = getLastURI(res_list)
    #print("related_resource:",related_resource)
    for resource in related_resource:
        senzai_resource = kks.convert(resource)
        senzai = ''.join([item['kana'] for item in senzai_resource])
        #print("cand_kg_label",cand_kg_label)
        #print("senzai:",senzai)
        #print("変形表現:",cwm_text)
        if len(cwm_text) >=2 and len(senzai) >=2:
            if ls.jaro_winkler(cwm_text, senzai) >= 0.95:
                return (cwm_text, resource) #変形表現,潜在表現
            
    return ("","")



def find_resource_list(cwml, url=URL_LIST[0]):
    """URLから構成されたリソースURIのリストを返す"""
    res_list = []
    for cwm in cwml: #ConceptNetでリソースが存在するかをチェックする
        res_list.append(url + "/c/ja/" + cwm.lemma_)
    return res_list


def find_latent_expression2(org_res_label, tane_index, res_list, depth, tane_lst, tane_kana_lst, tane_element_lst, henkei_lst, henkei_element_lst, latent_expression_cand_dict = dict()):
    """対象知識グラフより潜在表現を探索し，音韻類似により検出する再帰関数"""
    tane = ""
    senzai = ""
    henkei = ""
    related_res_list = []

    # 深さが2を上回る場合は探索しない
    if depth > 2:
        return tane, senzai, henkei

    if tane_index == None:
        tane_index = 0
        #print("res_list",res_list)
        for r in res_list:
            # 潜在表現候補を追加
            #print("==============================================================")
            #print("depth:",depth)
            #print("org_res_label:",org_res_label)
            #print("r:",r)
            lecd, rr_list = find_latent_expression_candidates(r, org_res_label, depth)
            #print("rr_list:",rr_list)
            related_res_list.append(rr_list)
            # 内容語との音韻比較
            henkei_index = 0
            for h in henkei_lst:
                #print("tane_index:",tane_index)
                #print("henkei_index:",henkei_index)
                if all(num not in tane_element_lst[tane_index] for num in henkei_element_lst[henkei_index]):
                    #print("変形表現:",h)
                    #print("変形表現の要素",henkei_element_lst[henkei_index])
                    #print("潜在表現のリスト:",latent_expression_cand_dict)
                    #print("related_res_list:",related_res_list)
                    tane = tane_lst[tane_index]
                    henkei, senzai = detect_latent_expression(h, rr_list)
                    if ls.jaro_winkler(tane_kana_lst[tane_index][0],h) < 0.5:
                        # 潜在表現が検出できれば，これをreturnする --> 検出成功，終了
                        if senzai:
                            #print("=====================================================")
                            #ic(cwm)
                            return tane, henkei, senzai
                henkei_index = henkei_index + 1
            tane_index = tane_index + 1

    elif tane_index != None:
        for r in res_list:
            # 潜在表現候補を追加
            #print("===============================================================")
            #print("depth:",depth)
            #print("org_res_label:",org_res_label)
            #print("res_list:",r)
            lecd, rr_list = find_latent_expression_candidates(r, org_res_label, depth)
            #print("rr_list:",rr_list)
            related_res_list.append(rr_list)
            # 内容語との音韻比較
            henkei_index = 0
            for h in henkei_lst:
                #print("tane_index:",tane_index)
                #print("henkei_index:",henkei_index)
                if all(num not in tane_element_lst[tane_index] for num in henkei_element_lst[henkei_index]):
                    #print("変形表現:",h)
                    #print("変形表現の要素",henkei_element_lst[henkei_index])
                    #print("潜在表現のリスト:",latent_expression_cand_dict)
                    #print("related_res_list:",related_res_list)
                    tane = tane_lst[tane_index]
                    henkei, senzai = detect_latent_expression(h, rr_list)
                    if ls.jaro_winkler(tane_kana_lst[tane_index][0],h) < 0.5:
                        # 潜在表現が検出できれば，これをreturnする --> 検出成功，終了
                        if senzai:
                            #print("=====================================================")
                            #ic(cwm)
                            return tane, henkei, senzai
                henkei_index = henkei_index + 1

    #ic(related_res_list)
    # TODO: ここの再帰に入ることができていないので修正すべき． --> 20211215修正． find_resource_list() でのURI生成間違いが原因だった
    # ここまでで検出に成功していない場合（深さが2以下），幅優先探索として再帰的に他の潜在表現候補を求める
    for i, r_list in enumerate(related_res_list):
        if org_res_label == "":
            tane_index = i
            org_res_label = tane_lst[i].text
        return find_latent_expression2(org_res_label, tane_index, r_list, depth+1, tane_lst, tane_kana_lst, tane_element_lst, henkei_lst, henkei_element_lst, latent_expression_cand_dict)

    return "", "", ""



#メインの処理
# 
def new_conceptnet(dajare):
    """メイン関数"""

    for url in URL_LIST:  # url_list: SPARQL endpoints (or Web API) of Knowledge graphs
        tane_lst, tane_kana_lst, tane_element_lst, henkei_lst, henkei_element_lst = find_tane_henkei_list(dajare)
        found = False
        latent_expressions = list()
        res_list = find_resource_list(tane_lst)  # リソースURIのリスト
        #print("Resource list", res_list) #種表現とそのURI

        tane, henkei, senzai = find_latent_expression2("", None, res_list, 1, tane_lst, tane_kana_lst, tane_element_lst, henkei_lst, henkei_element_lst, dict())
        #print("latent_expressions:",latent_expressions)
        #ic(latent_expression_cand_dict)

        if senzai:
            
            print("成功　駄洒落文：", dajare, "種表現", tane, "潜在表現：", senzai, "変形表現：",henkei)
            detected = '成功'
            return(detected, tane, senzai, henkei)
        else:
            print("失敗")
            detected = '失敗'
            tane = 'なし'
            senzai = 'なし'
            henkei = 'なし'
            return(detected, tane, senzai, henkei)

if __name__ == "__main__":
    """プログラムの実行，
    
    コマンドライン引数で整数値を指定すると，ConceptNetへの問い合わせ時にクエリパラメータとして取得数上限を指定する．"""
    #TODO: Usageを現状の使い方に沿うよう修正
    #TODO: main()の関数名を適切なものに変更し，このブロックをmain()にする
    #if len(sys.argv) < 2:
        ##print("Usage:\n    python latent_detect.py <text file name>")
       # sys.exit(1)
    #input_sentence = sys.argv[1]

    #if len(sys.argv) > 1:
    #    PARAM_LIMIT = "?limit=" + sys.argv[1]
    PARAM_LIMIT = "?limit=" + LIMIT
    filepath_output = "output_humor.txt"
    open(filepath_output, 'w').close()
    # conceptnet(dajare, filepath_output)
    