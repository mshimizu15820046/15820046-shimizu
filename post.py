#重畳型
import requests
import json

#POST先URL
url = "http://localhost:5000/chive"
url2 = "http://localhost:5000/entity"
url3 = "http://localhost:5000/conceptnet"
url4 = "http://localhost:5000/kana"
url5 = "http://localhost:5000/heichi"　#追加


newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}

from json import load

#input.txtの1~68行目を実験の対象に設定
for a in range(68):
  file_name = 'input.txt'

  with open(file_name) as f:
    lines = f.readlines()[a].strip()
    print('=====================================================================================')
    print()
    #JSON形式のデータ
    json_data = {
        "dajare": lines
    }

    #POST送信(chiVe)
    response = requests.post(
        url,
        data = json.dumps(json_data),    #dataを指定する
        headers = newHeaders 
        )

    
    #POST送信2(Wikipedia Entity Vectors)
    response2 = requests.post(
        url2,
        data = json.dumps(json_data),    #dataを指定する
        headers = newHeaders 
        )

    #POST送信3(ConceptNet)
    response3 = requests.post(
        url3,
        data = json.dumps(json_data),    #dataを指定する
        headers = newHeaders 
        )
    
    #POST送信4(かな漢字変換)
    response4 = requests.post(
        url4,
        data = json.dumps(json_data),    #dataを指定する
        headers = newHeaders 
        )

    #POST送信5(併置型判定)　　　　　#追加
    repsonse5 = requests.post(
        url5,
        data = json.dumps(json_data),    #dataを指定する
        headers = newHeaders 
    )


    res_data = response.json()
    res_data2 = response2.json()
    res_data3 = response3.json()
    res_data4 = response4.json()
    res_data5 = response5.json() #追加

    print('駄洒落文：' + res_data["lines"])
    print()
    print('chiVeでの検出結果：' + res_data["result"])
    print('内容語：' + res_data["henkei"])
    print('潜在表現：' + res_data["senzai"])
    print(res_data["henkei"] , 'と' , res_data["senzai"] , 'のコサイン類似度：' , res_data["sim"])
    print()

    print('Wikipedia Entity Vectorでの検出結果：' + res_data2["result"])
    print('内容語：' + res_data2["henkei"])
    print('潜在表現：' + res_data2["senzai"])
    print(res_data2["henkei"] , 'と' , res_data2["senzai"] , 'のコサイン類似度：' , res_data2["sim"])
    print()

    print('ConceptNetでの検出結果：' + res_data3["result"])
    print('内容語：' + res_data3["henkei"])
    print('潜在表現：' + res_data3["senzai"])
    print()

    print('かな漢字変換での検出結果：' + res_data4["result"])
    print('内容語：' + res_data4["henkei"])
    print('潜在表現：' + res_data4["senzai"])
    print(res_data4["henkei"] , 'と' , res_data4["senzai"] , 'のコサイン類似度：' , res_data4["sim"])
    print()

    s = res_data["result"], res_data2["result"], res_data3["result"], res_data4["result"]
    print(s)
    #「成功」が2つ以上の手法で取得されたら検出成功
    if s.count('成功') >= 2:
        print('\033[32m'+ '検出成功' +'\033[0m')
    else:
        print('\033[31m'+'検出失敗'+'\033[0m')

    json_data = f.readline() #次の行を読み込む


