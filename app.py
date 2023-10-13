#重畳型
from flask import Flask, request, jsonify
from chive import chive
from entity import entity
from conceptnet import conceptnet
from kana import kana
import json
app = Flask(__name__)

#単語埋め込み(chiVe)を用いた手法
@app.route('/chive', methods=['GET', 'POST'])
def chive_example():
    if request.method == 'POST':
        dajare = request.json['dajare']  # データが空の場合 None
        print(dajare)
        if not dajare:
            return jsonify(result=None, message='No input')
        detected, senzai, henkei, sim, lines = chive(dajare)
        # chive() の出力を下記のように仮定しています：
        # detected: 検出成功の場合 True
        # senzai: 「鮭の卵は、いくら？」における「鮭」
        # henkei: (同上)「いくら」
        # sim:    (同上)「鮭」と「イクラ」の意味類似度
        return jsonify(result=detected, senzai=senzai, henkei=henkei, sim=sim, lines=lines, message='OK')  # 通常出力
        
    # GETメソッドの場合
    return jsonify(result=None, message='Only POST method is accepted')

#単語埋め込み(Wikipedia Entity Vectors)を用いた手法
@app.route('/entity', methods=['GET', 'POST'])
def entity_example():
    if request.method == 'POST':
        dajare = request.json['dajare']  # データが空の場合 None
        if not dajare:
            return jsonify(result=None, message='No input')
        detected, senzai, henkei, sim = entity(dajare)
        return jsonify(result=detected, senzai=senzai, henkei=henkei, sim=sim, message='OK')  # 通常出力
        
    # GETメソッドの場合
    return jsonify(result=None, message='Only POST method is accepted')

#知識グラフを用いた手法
@app.route('/conceptnet', methods=['GET', 'POST'])
def conceptnet_example():
    if request.method == 'POST':
        dajare = request.json['dajare']  # データが空の場合 None
        if not dajare:
            return jsonify(result=None, message='No input')
        detected, senzai, henkei = conceptnet(dajare)
        return jsonify(result=detected, senzai=senzai, henkei=henkei, message='OK')  # 通常出力
        
    # GETメソッドの場合
    return jsonify(result=None, message='Only POST method is accepted')

#かな漢字変換を用いた手法
@app.route('/kana', methods=['GET', 'POST'])
def kana_example():
    if request.method == 'POST':
        dajare = request.json['dajare']  # データが空の場合 None
        if not dajare:
            return jsonify(result=None, message='No input')
        detected, senzai, henkei, sim = kana(dajare)
        return jsonify(result=detected, senzai=senzai, henkei=henkei, sim=sim, message='OK')  # 通常出力
        
    # GETメソッドの場合
    return jsonify(result=None, message='Only POST method is accepted')

#併置型駄洒落の判定　　　#追加
@app.route('/heichi', methods=['GET', 'POST'])
def heichi_example():
    if request.method == 'POST':
        dajare = request.json['dajare']  # データが空の場合 None
        if not dajare:
            return jsonify(result=None, message='No input')
        detected, senzai, henkei, sim = kana(dajare)
        return jsonify(result=detected, senzai=senzai, henkei=henkei, sim=sim, message='OK')  # 通常出力
        
    # GETメソッドの場合
    return jsonify(result=None, message='Only POST method is accepted')

if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run(threaded=True)
    