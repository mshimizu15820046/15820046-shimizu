#重畳型
from chive import chive
from entity import entity
from conceptnet import conceptnet
from kana import kana
from dajare_recognition import heich

for a in range(68):
    file_name = 'new_input.txt'

    with open(file_name) as f:
        lines = f.readlines()[a].strip()
        print('=====================================================================================')
        print('駄洒落文：' + lines)
        detected1, senzai1, henkei1, sim1, lines1 = chive(lines)
        print('重畳型駄洒落か検証')
        print()
        print('chiVeでの検出結果：' + detected1)
        print('内容語：' + henkei1)
        print('潜在表現：' + senzai1)
        print(henkei1 , 'と' , senzai1 , 'のコサイン類似度：' , sim1)

        print()
        detected2, senzai2, henkei2, sim2 = entity(lines)
        print('Wikipedia Entity Vectorでの検出結果：' + detected2)
        print('内容語：' + henkei2)
        print('潜在表現：' + senzai2)
        print(henkei2 , 'と' , senzai2 , 'のコサイン類似度：' , sim2)

        print()
        detected3, senzai3, henkei3 = conceptnet(lines)
        print('ConceptNetでの検出結果：' + detected3)
        print('内容語：' + henkei3)
        print('潜在表現：' + senzai3)

        print()
        detected4, senzai4, henkei4, sim4 = kana(lines)
        print('かな漢字変換での検出結果：' + detected4)
        print('内容語：' + henkei4)
        print('潜在表現：' + senzai4)
        print(henkei4 , 'と' , senzai4 , 'のコサイン類似度：' , sim4)
        print()

        s = detected1, detected2, detected3, detected4
        print(s)
        #「成功」が2つ以上の手法で取得されたら検出成功
        if s.count('成功') >= 2:
            print('\033[32m'+ '検出成功' +'\033[0m')
        else:
            print('\033[31m'+'検出失敗'+'\033[0m')
        
        print()
        print('併置型駄洒落か検証')
        detected4, tane_word, henkei_word = heich(lines)
        print('判定結果：' + detected4)
        print('主表現：' + tane_word)
        print('変形表現：' + henkei_word)
        print()


        

