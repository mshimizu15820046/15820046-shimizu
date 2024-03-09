## 事前準備
* pip install -r requirements.txt　を実行
* chiVe：https://github.com/WorksApplications/chiVe
         (v1.2-mc5(gensim)をダウンロード)
* Wikipedia Entity Vectors：http://www.cl.ecei.tohoku.ac.jp/~m-suzuki/jawiki_vector/
                            (20170201.tar.bz2 をダウンロード)

## 実行方法

### 併置型駄洒落の認識
new_dajare_recognition.pyを実行することで入力文が併置型駄洒落か判定できる.(detected, type は既存手法での判定, detectede_m, type_m は本手法での判定)

### 重畳型駄洒落の認識

#### chiVeを用いた手法
new_chive.pyを実行することで入力文が重畳型駄洒落か判定できる.

#### Wikipedia Entity Vectorsを用いた手法
new_entity.pyを実行することで入力文が重畳型駄洒落か判定できる.

#### 知識グラフを用いた手法
new_conceptnet.pyを実行することで入力文が重畳型駄洒落か判定できる.

#### かな漢字変換を用いた手法
new_kana.pyを実行することで入力文が重畳型駄洒落か判定できる.

#### 統合したシステム
new_app.pyを実行することでデータセット内の文が併置型駄洒落か重畳型駄洒落か駄洒落ではない文かを判定することができる.

### データセット
csvファイルにid,sentence,tane,henkei,typeの順でテキストを入力.
