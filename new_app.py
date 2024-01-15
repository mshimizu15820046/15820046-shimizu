#重畳型
from chive import chive
from entity import entity
from new_conceptnet import new_conceptnet
from kana import kana
from new_dajare_recognition import heich
import pandas as pd
from new_chive import new_chive
from new_entity import new_entity


#data = pd.read_csv("./dajare_database1.csv", encoding="cp932")
#data = pd.read_csv("./dajare_database2.csv")
data = pd.read_csv("./dajare_database4.csv")
#data = pd.read_csv("./dajare_h_database.csv")
#data = pd.read_csv("./dajare_database_test.csv")

d_num = 0 #csv上の文章の数
correct_tanehenkei_num = 0
correct_type_num = 0
correct_put_num = 0
correct_super_num = 0
correct_normal_num = 0
m_correct_type_num = 0
m_correct_put_num = 0
m_correct_super_num = 0
m_correct_normal_num = 0
per_tanehenkei = 0
per_type = 0
per_type_super = 0
per_type_put = 0
super_num = 0 #csv上の重畳型駄洒落の数
put_num = 0 #csv上の併置型駄洒落の数
normal_num = 0 #csv上の駄洒落ではない文の数
put_num_res = 0 #併置型と判定された数
super_num_res = 0 #重畳型と判定された数
normal_num_res = 0 #駄洒落ではないと判定された数
precision_put = 0 #併置型の適合率
recall_put = 0 #併置型の再現率
f_measure_put = 0 #併置型のF値
precision_super = 0 #重畳型の適合率
recall_super = 0 #重畳型の再現率
f_measure_super = 0 #重畳型のF1値
precision_normal = 0 #駄洒落ではない文の適合率
recall_normal = 0 #駄洒落ではない文の再現率
f_measure_normal = 0 #駄洒落ではない文のF値

m_put_num_res = 0 #併置型と判定された数(文字単位)
m_super_num_res = 0 #重畳型と判定された数(文字単位)
m_normal_num_res = 0 #駄洒落ではないと判定された数(文字単位)
m_precision_put = 0 #併置型の適合率(文字単位)
m_recall_put = 0 #併置型の再現率(文字単位)
m_f_measure_put = 0 #併置型のF値(文字単位)
m_precision_super = 0 #重畳型の適合率(文字単位)
m_recall_super = 0 #重畳型の再現率(文字単位)
m_f_measure_super = 0 #重畳型のF1値(文字単位)
m_precision_normal = 0 #駄洒落ではない文の適合率(文字単位)
m_recall_normal = 0 #駄洒落ではない文の再現率(文字単位)
m_f_measure_normal = 0 #駄洒落ではない文のF値(文字単位)

type = "不明"
type_m = "不明"

for i in range(len(data)):
    for j in data.columns[0:5:1]:
        if j == "id":
            d_num = d_num + 1
            print('=====================================================================================')
            id = data.at[i,j]
            print("id:",id)
        elif j == "sentence":
            print('駄洒落文：',data.at[i,j])
            text = data.at[i,j]
            print()
            print('併置型駄洒落か検証')
            detected, detected_m, tane_word, henkei_word, rank_tane_lst, rank_henkei_lst, rank_thres_lst, type, type_m = heich(text)
            if detected=='成功':
                print('判定結果：' + '\033[32m' + detected + '\033[0m')
            else:
                print('判定結果：' + '\033[31m' + detected + '\033[0m')
            print('種表現：' + tane_word)
            print('変形表現：' + henkei_word)
            print()
        elif j == "tane":
            tane_ans = data.at[i,j]
            tane_txt_lst = []
            del_lst = []
            for k in range(len(tane_ans)):
                tane_txt_lst.append(tane_ans[k])
            for k in range(len(tane_txt_lst)):
                if tane_txt_lst[k] == '<' and k not in del_lst:
                    del_lst.append(k)
                    for l in range(k+1, len(tane_txt_lst),1):
                        if tane_txt_lst[l] != '>' and tane_txt_lst[l] != '＞' and tane_txt_lst[l] != ')' and tane_txt_lst[l] !='）':
                            del_lst.append(l)
                        else:
                            del_lst.append(l)
                            break;
                if tane_txt_lst[k] == '＜' and k not in del_lst:
                    del_lst.append(k)
                    for l in range(k+1, len(tane_txt_lst),1):
                        if tane_txt_lst[l] != '>' and tane_txt_lst[l] != '＞' and tane_txt_lst[l] != ')' and tane_txt_lst[l] !='）':
                            del_lst.append(l)
                        else:
                            del_lst.append(l)
                            break;
                if tane_txt_lst[k] == '（' and k not in del_lst:
                    del_lst.append(k)
                    for l in range(k+1, len(tane_txt_lst),1):
                        if tane_txt_lst[l] != '>' and tane_txt_lst[l] != '＞' and tane_txt_lst[l] != ')' and tane_txt_lst[l] !='）':
                            del_lst.append(l)
                        else:
                            del_lst.append(l)
                            break;
                if tane_txt_lst[k] == '(' and k not in del_lst:
                    del_lst.append(k)
                    for l in range(k+1, len(tane_txt_lst),1):
                        if tane_txt_lst[l] != '>' and tane_txt_lst[l] != '＞' and tane_txt_lst[l] != ')' and tane_txt_lst[l] !='）':
                            del_lst.append(l)
                        else:
                            del_lst.append(l)
                            break;
            if del_lst:
                print("種表現del_lst:",del_lst)
                for k in sorted(del_lst, reverse=True):
                    tane_txt_lst.pop(k)
            tane_ans = ''.join(tane_txt_lst)
            print("理想の種表現:",tane_ans)
        elif j == "henkei":
            henkei_ans = data.at[i,j]
            henkei_txt_lst = []
            del_lst = []
            for k in range(len(henkei_ans)):
                henkei_txt_lst.append(henkei_ans[k])
            for k in range(len(henkei_txt_lst)):
                if henkei_txt_lst[k] == '、' and k not in del_lst:
                    del_lst.append(k)
                if henkei_txt_lst[k] == '<' and k not in del_lst:
                    del_lst.append(k)
                    for l in range(k+1, len(henkei_txt_lst),1):
                        if henkei_txt_lst[l] != '>' and henkei_txt_lst[l] != '＞' and henkei_txt_lst[l] != ')' and henkei_txt_lst[l] !='）':
                            del_lst.append(l)
                        else:
                            del_lst.append(l)
                            break;
                if henkei_txt_lst[k] == '＜' and k not in del_lst:
                    del_lst.append(k)
                    for l in range(k+1, len(henkei_txt_lst),1):
                        if henkei_txt_lst[l] != '>' and henkei_txt_lst[l] != '＞' and henkei_txt_lst[l] != ')' and henkei_txt_lst[l] !='）':
                            del_lst.append(l)
                        else:
                            del_lst.append(l)
                            break;
                if henkei_txt_lst[k] == '(' and k not in del_lst:
                    del_lst.append(k)
                    for l in range(k+1, len(henkei_txt_lst),1):
                        if henkei_txt_lst[l] != '>' and henkei_txt_lst[l] != '＞' and henkei_txt_lst[l] != ')' and henkei_txt_lst[l] !='）':
                            del_lst.append(l)
                        else:
                            del_lst.append(l)
                            break;
                if henkei_txt_lst[k] == '（' and k not in del_lst:
                    del_lst.append(k)
                    for l in range(k+1, len(henkei_txt_lst),1):
                        if henkei_txt_lst[l] != '>' and henkei_txt_lst[l] != '＞' and henkei_txt_lst[l] != ')' and henkei_txt_lst[l] !='）':
                            del_lst.append(l)
                        else:
                            del_lst.append(l)
                            break;
            if del_lst:
                print("変形表現del_lst:",del_lst)
                for k in sorted(del_lst, reverse=True):
                    henkei_txt_lst.pop(k)
            henkei_ans = ''.join(henkei_txt_lst)
            print("理想の変形表現:",henkei_ans)
        elif j == "type":
            type_ans = data.at[i,j]
            if type_ans == "併置型":
                put_num = put_num + 1
            elif type_ans == "重畳型":
                super_num = super_num + 1
            elif type_ans == "不明":
                normal_num = normal_num + 1
    for j in range(len(rank_tane_lst)):
        if tane_ans == rank_tane_lst[j] and henkei_ans == rank_henkei_lst[j]:
            correct_tanehenkei_num = correct_tanehenkei_num + 1

    print()

    for j in data.columns[1:5:1]:
        if j == "sentence":
            print("重畳型駄洒落か検証")
            text = data.at[i,j]
            detected1, tane1, senzai1, henkei1, sim1 = new_chive(text)
            print('chiVeでの検出結果：' + detected1)
            print('種表現：', tane1)
            print('潜在表現：', senzai1)
            print('変形表現：', henkei1)
            print(henkei1 , 'と' , senzai1 , 'の類似度：' , sim1)
            print()
            detected2, tane2, senzai2, henkei2, sim2 = new_entity(text)
            print('Wikipedia Entity Vectorでの検出結果：', detected2)
            print('種表現：', tane2)
            print('潜在表現：', senzai2)
            print('変形表現：', henkei2)
            print(henkei2 , 'と' , senzai2 , 'の類似度：' , sim2)

            print()
            detected3, tane3, senzai3, henkei3 = new_conceptnet(text)
            print('ConceptNetでの検出結果：' + detected3)
            print('種表現：', tane3)
            print('潜在表現：', senzai3)
            print('変形表現：', henkei3)

            print()
            detected4, senzai4, henkei4, sim4 = kana(text)
            print('かな漢字変換：', detected4)
            print('潜在表現：',senzai4)
            print('変形表現：',henkei4)
            print(henkei4 , 'と' , senzai4 , 'のコサイン類似度：' , sim4)

            s = detected1, detected2, detected3, detected4
            print(s)
            #「成功」が2つ以上の手法で取得されたら検出成功
            if s.count('成功') >= 2:
                print('\033[32m'+ '検出成功' +'\033[0m')
                if type == "併置型":
                    type = "併置型かつ重畳型"
                else:
                    type = "重畳型"
                
                if type_m == "併置型":
                    type_m = "併置型かつ重畳型"
                else:
                    type_m = "重畳型"
            else:
                print('\033[31m' + '検出失敗' + '\033[0m')
        if j == "type":
            print()
            print("理想的な型:",type_ans)

    print("形態素形式での結果:",type)
    print("文字形式での結果:",type_m)

    #正しく検出された数(形態素)
    if type == type_ans or (type_ans == "併置型" and type == "併置型かつ重畳型") or (type_ans == "重畳型" and type == "併置型かつ重畳型"):
        correct_type_num = correct_type_num + 1
    if (type == "併置型" and type_ans == "併置型") or (type == "併置型かつ重畳型" and type_ans == "併置型"):
        correct_put_num = correct_put_num + 1
    if (type == "重畳型" and type_ans == "重畳型") or (type == "併置型かつ重畳型" and type_ans == "重畳型"):
        correct_super_num = correct_super_num + 1
    if (type =="不明" and type_ans == "不明"):
        correct_normal_num = correct_normal_num + 1
    
    #検出された数(形態素)
    if type == "併置型" or type == "併置型かつ重畳型":
        put_num_res = put_num_res + 1
    if type == "重畳型" or type == "併置型かつ重畳型":
        super_num_res = super_num_res + 1
    if type == "不明":
        normal_num_res = normal_num_res + 1

    #正しく検出された数(文字)
    if type_m == type_ans or (type_ans == "併置型" and type_m == "併置型かつ重畳型") or (type_ans == "重畳型" and type_m == "併置型かつ重畳型"):
        m_correct_type_num = m_correct_type_num + 1
    if (type_m == "併置型" and type_ans == "併置型") or (type_m == "併置型かつ重畳型" and type_ans == "併置型"):
        m_correct_put_num = m_correct_put_num + 1
    if (type_m == "重畳型" and type_ans == "重畳型") or (type_m == "併置型かつ重畳型" and type_ans == "重畳型"):
        m_correct_super_num = m_correct_super_num + 1
    if (type_m =="不明" and type_ans == "不明"):
        m_correct_normal_num = m_correct_normal_num + 1
    
    #検出された数(文字)
    if type_m == "併置型" or type_m == "併置型かつ重畳型":
        m_put_num_res = m_put_num_res + 1
    if type_m == "重畳型" or type_m == "併置型かつ重畳型":
        m_super_num_res = m_super_num_res + 1
    if type_m == "不明":
        m_normal_num_res = m_normal_num_res + 1

#併置型 (形態素)
precision_put = correct_put_num / put_num_res
recall_put = correct_put_num / put_num
f_measure_put = 2 * precision_put * recall_put / (precision_put + recall_put)
#重畳型 (形態素)
precision_super = correct_super_num / super_num_res
recall_super = correct_super_num / super_num
f_measure_super = 2 * precision_super * recall_super / (precision_super + recall_super)
#駄洒落ではない (形態素)
precision_normal = correct_normal_num / normal_num_res
recall_normal = correct_normal_num / normal_num
f_measure_normal = 2 * precision_normal * recall_normal / (precision_normal + recall_normal)

#併置型 (文字)
m_precision_put = m_correct_put_num / m_put_num_res
m_recall_put = m_correct_put_num / put_num
m_f_measure_put = 2 * m_precision_put * m_recall_put / (m_precision_put + m_recall_put)
#重畳型 (文字)
m_precision_super = m_correct_super_num / m_super_num_res
m_recall_super = m_correct_super_num / super_num
m_f_measure_super = 2 * m_precision_super * m_recall_super / (m_precision_super + m_recall_super)
#駄洒落ではない (文字)
m_precision_normal = m_correct_normal_num / m_normal_num_res
m_recall_normal = m_correct_normal_num / normal_num
m_f_measure_normal = 2 * m_precision_normal * m_recall_normal / (m_precision_normal + m_recall_normal)

print("")
print("形態素単位で併置型と判定された数:",put_num_res)
print("形態素単位で重畳型と判定された数:",super_num_res)
print("形態素単位で駄洒落ではないと判定された数:",normal_num_res)
print("形態素単位で正しく併置型と判定された数:",correct_put_num)
print("形態素単位で正しく重畳型と判定された数:",correct_super_num)
print("形態素単位で正しく駄洒落ではないと判定された数:",correct_normal_num)
print("")
print("文字単位で併置型と判定された数:",m_put_num_res)
print("文字単位で重畳型と判定された数:",m_super_num_res)
print("文字単位で駄洒落ではないと判定された数:",m_normal_num_res)
print("文字単位で正しく併置型と判定された数:",m_correct_put_num)
print("文字単位で正しく重畳型と判定された数:",m_correct_super_num)
print("文字単位で正しく駄洒落ではないと判定された数:",m_correct_normal_num)
print("")
print("形態素単位")
print("併置型駄洒落の適合率:",precision_put)
print("併置型駄洒落の再現率:",recall_put)
print("併置型駄洒落のF値:",f_measure_put)
print("重畳型駄洒落の適合率:",precision_super)
print("重畳型駄洒落の再現率:",recall_super)
print("重畳型駄洒落のF値:",f_measure_super)
print("駄洒落ではない文の適合率:",precision_normal)
print("駄洒落ではない文の再現率:",recall_normal)
print("駄洒落ではない文のF値:",f_measure_normal)
print("")
print("文字単位")
print("併置型駄洒落の適合率:",m_precision_put)
print("併置型駄洒落の再現率:",m_recall_put)
print("併置型駄洒落のF値:",m_f_measure_put)
print("重畳型駄洒落の適合率:",m_precision_super)
print("重畳型駄洒落の再現率:",m_recall_super)
print("重畳型駄洒落のF値:",m_f_measure_super)
print("駄洒落ではない文の適合率:",m_precision_normal)
print("駄洒落ではない文の再現率:",m_recall_normal)
print("駄洒落ではない文のF値:",m_f_measure_normal)
