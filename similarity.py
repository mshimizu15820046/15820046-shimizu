import pykakasi
from distanceutil import EditDistanceUtil
THETA = 0.50

def similarity(text1,text2):

    kks = pykakasi.kakasi()
    edu = EditDistanceUtil()

    hira1 = "".join(d["kana"] for d in kks.convert(text1))
    hira2 = "".join(d["kana"] for d in kks.convert(text2))
    
    #print(text1,hira1)
    #print(text2,hira2)
    
    result = edu.calc_ed(hira1, hira2, is_relative=False, ed_type="normal", kana_type="kana")
    return 1.0/(result+1)


def similar(text1,text2):
    #print(similarity(text1,text2))
    #print(text1,text2)
    return similarity(text1,text2) >= THETA

if __name__ == "__main__":
    print(similarity('いくら','イクラ'))
    #similarity('脳','農作業')
