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

from similarity import *

nlp = spacy.load('ja_ginza')
#nlp = spacy.load('ja_ginza_electra')
ginza.set_split_mode(nlp, 'C') # 形態素解析：分割単位の設定 (形態素長さ: A < B < C)

URL_LIST = ['http://api.conceptnet.io']  # Knowledge graph URLs
#URL_LIST = ['http://133.2.207.190:8084']  # Local ConceptNet5 API

PARAM_LIMIT = ""  # 空のままにすること
LIMIT = "20"  # 20件がデフォルト


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



def detect_latent_expression(cwm, cand_dict):
    detected_candidates = list()
    cwm_text = cwm.text

    for cand_label, cand_set in cand_dict.items():
        if cand_label == cwm_text:
            continue
        #ic(cand_label,  cand_set) 
        for cand in cand_set:
            cand_kg_label = cand.getLatentExpLabel()
            try:
                if similar(cwm_text, cand_kg_label):
                    #print(f"類似検出| 内容語={cwm_text}, 潜在表現候補={cand_kg_label}")
                    #ic(cand)
                    detected_candidates.append(cand)
                    #print("検出=====================================================")
                    ##print(cwm_text, cand_kg_label, cand.org_res_label)
                    #print(cand)
                    return detected_candidates
            except IndexError:
                #print(f"類似失敗| IndexError! Similar: {cwm_text}, {cand_kg_label}")
                return []
    return detected_candidates



def find_resource_list(cwml, url=URL_LIST[0]):
    """URLから構成されたリソースURIのリストを返す"""
    res_list = []
    for cwm in cwml: #ConceptNetでリソースが存在するかをチェックする
        res_list.append(url + "/c/ja/" + cwm.lemma_)
    return res_list


def find_latent_expression2(org_res_label, res_list, cwml, depth, latent_expression_cand_dict = dict()):
    """対象知識グラフより潜在表現を探索し，音韻類似により検出する再帰関数"""
    latent_expressions = []
    related_res_list = []

    # 深さが2を上回る場合は探索しない
    if depth > 2:
        return latent_expressions, latent_expression_cand_dict

    for r in res_list:
        # 潜在表現候補を追加
        lecd, rr_list = find_latent_expression_candidates(r, org_res_label, depth)
        for key_word, val_set in lecd.items():
            if key_word not in latent_expression_cand_dict.keys():
                latent_expression_cand_dict[key_word] = val_set
            else:
                latent_expression_cand_dict[key_word] |= val_set  # 含まれていなかったものを追加
        related_res_list.append(rr_list)
        # 内容語との音韻比較
        for cwm in cwml:
            latent_expressions = detect_latent_expression(cwm, latent_expression_cand_dict)
            # 潜在表現が検出できれば，これをreturnする --> 検出成功，終了
            if latent_expressions:
                #print("=====================================================")
                #ic(cwm)
                return latent_expressions, latent_expression_cand_dict

    #ic(related_res_list)
    # TODO: ここの再帰に入ることができていないので修正すべき． --> 20211215修正． find_resource_list() でのURI生成間違いが原因だった
    # ここまでで検出に成功していない場合（深さが2以下），幅優先探索として再帰的に他の潜在表現候補を求める
    for i, r_list in enumerate(related_res_list):
        if org_res_label == "":
            #ic(org_res_label)
            org_res_label = cwml[i].text
        return find_latent_expression2(org_res_label, r_list, cwml, depth+1, latent_expression_cand_dict)

    return [], {}



#メインの処理
# 
def conceptnet(dajare, filepath_output="output_humor.txt"):
    """メイン関数"""
    #f_write = codecs.open(filepath_output, 'a')

    for url in URL_LIST:  # url_list: SPARQL endpoints (or Web API) of Knowledge graphs
        cwml = find_content_word_morpheme_list(dajare)
        #print("形態素内容語:",cwml)
        found = False
        latent_expressions = list()
        res_list = find_resource_list(cwml)  # リソースURIのリスト
        #print("Resource list", res_list)

        latent_expressions, latent_expression_cand_dict = find_latent_expression2("", res_list, cwml, 1, dict())
        #ic(latent_expression_cand_dict)

        if latent_expressions:
            cand = latent_expressions[0]
            latent_exp, contentword, predicate, depth, direction,org_res_label = cand.getLatentExp(), cand.getContentWord(), cand.relation, cand.depth, cand.place, cand.org_res_label
                
            content_word = ""
            #ic(latent_expressions[0])
            #print(f"駄洒落文：{dajare}\n深さ：{depth} 内容語：{org_res_label} 関係性：{predicate} 向き：{direction} 検出結果：{latent_exp} \n",file=f_write)
            #f_write.flush()
            detected = '成功'
            senzai = latent_exp
            henkei = org_res_label
            return(detected, senzai, henkei)
        else:
            print("失敗")
            detected = '失敗'
            senzai = 'なし'
            henkei = 'なし'
            return(detected, senzai, henkei)
    
    #f_write.close()

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
    