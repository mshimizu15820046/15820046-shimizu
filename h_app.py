#併置型
from dajare_recognition import heich
import pandas as pd

#data = pd.read_csv("./dajare_database1.csv", encoding="cp932")
#data = pd.read_csv("./dajare_database2.csv")
#data = pd.read_csv("./dajare_h_database.csv")
data = pd.read_csv("./dajare_database3.csv")

d_num = 0 #csv上の文章の数
correct_tanehenkei_num = 0
correct_type_num = 0
correct_put_num = 0
correct_super_num = 0
per_tanehenkei = 0
per_type = 0
super_num = 0 #csv上の重畳型駄洒落の数
put_num = 0 #csv上の併置型駄洒落の数
normal_num = 0 #csv上の駄洒落ではない文の数
rank_tane_lst = []
rank_henkei_lst = []
rank_thres_lst = []
type_ans = ""

for i in range(len(data)):
    for j in data.columns[0:5:1]: #id, sentence, tane, henkei, type
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
            detected4, tane_word, henkei_word, rank_tane_lst, rank_henkei_lst, rank_thres_lst, type = heich(text)
            if detected4=='成功':
                print('判定結果：' + '\033[32m' + detected4 + '\033[0m')
            else:
                print('判定結果：' + '\033[31m' + detected4 + '\033[0m')
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
            print("理想的な型:",type_ans)
    for j in range(len(rank_tane_lst)):
        if tane_ans == rank_tane_lst[j] and henkei_ans == rank_henkei_lst[j]:
            correct_tanehenkei_num = correct_tanehenkei_num + 1
    if type == type_ans or (type_ans == "併置型" and type == "併置型かつ重畳型") or (type_ans == "重畳型" and type == "併置型かつ重畳型"):
        correct_type_num = correct_type_num + 1
    if (type == "併置型" and type_ans == "併置型") or (type == "併置型かつ重畳型" and type_ans == "併置型"):
        correct_put_num = correct_put_num + 1
    if (type == "重畳型" and type_ans == "重畳型") or (type == "併置型かつ重畳型" and type_ans == "重畳型"):
        correct_super_num = correct_super_num + 1

per_tanehenkei = (correct_tanehenkei_num / d_num) * 100
per_type =(correct_type_num / d_num) * 100
per_type_put = (correct_put_num / put_num) * 100

print("種表現と変形表現の正答率:",per_tanehenkei)
print("型の正答率:",per_type)
print("併置型駄洒落の正答率:",per_type_put)

            

'''
for a in range(68):
    file_name = 'new_input.txt'

    with open(file_name) as f:
        lines = f.readlines()[a].strip()
        print('=====================================================================================')
        print('駄洒落文：' + lines)
        print()
        print('併置型駄洒落か検証')
        detected4, tane_word, henkei_word = heich(lines)
        if detected4=='成功':
            print('判定結果：' + '\033[32m' + detected4 + '\033[0m')
        else:
            print('判定結果：' + '\033[31m' + detected4 + '\033[0m')
        print('種表現：' + tane_word)
        print('変形表現：' + henkei_word)
        print()
        '''

