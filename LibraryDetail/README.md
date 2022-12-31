# PlayerTracking.py

## 概要
OpenCVを使用して以下の処理を行う。  
    ①カメラからの画像の取得  
    ②指定した色のトラッキング  
    ③トラッキングデータの出力  

また、トラッキングする色の指定など、以下のメソッドを備える。  
    ①トラッキングする色の動的指定  
    ②指定した色情報の書き出し  
    ③既に書き出されている色情報の読み込み  

## PlayerTracking.pyの利用方法
```
from PlayerTracking import pt2
import PlayerTracking as PT

#pt2のインスタンス化
player = pt2()

#トラッキングする色の指定
player.set_color()

#カメラ画像をct2のクラス変数に代入する
while(PT.set_capture_read()):

    #トラッキング結果を取得する
    trackResultList = player.get_data()
```

## 詳細
* **クラス**
    * `pt2`  
        実際にインスタンス化するクラス  
        ct2とのインターフェイスの役目
    * `ct2`  
        OpenCVを用いてトラッキング処理を実装しているクラス
* **変数**
    * `pt2`
        * `self.ct2`  
            ct2クラスを移譲
        * `self.trackSize`  
            指定した色のトラッキングの結果を取得する個数
        * `self.beforeData`  
            前回のトラッキング結果を二次元配列に格納  
            [[重心x,　重心y, 左を起点とした横全体を1とする位置xの割合, 上を起点とした縦全体を1とする位置yの割合, 幅, 高さ, トラック領域の大きさ][...]...]
        * `self.currentData`  
            今回のトラッキング結果
    * `ct2`
        * `self.camera`(クラス変数)  
            OpenCV依存の実行環境のカメラ情報
        * `self.defaultCameraResolution`(クラス変数)  
            OpenCV依存の実行環境のカメラ解像度の初期値
        * `self.defaultFrame`(クラス変数)  
            カメラからの画像
        * `self.classFrame`(クラス変数)  
            HSV変換処理後のカメラ画像
        * `self.player`  
            HSVの色情報とトラッキング用の閾値を持つリスト
        * `self.playerInfo`  
            ct2メソッド用のフラグ  
            取得したHSVによって閾値の計算処理が変わるため
        * `self.mask`  
            カメラ画像内の指定色が存在する場所が白く、それ以外が黒くなった二値画像
* **メソッド**
    * `pt2`
        * `set_color(self, countTime = 5000)`  
            ct2.set_player_color()を実行する
        * `set_color_file(self, fileName)`  
            ColorDataというディレクトリからfilenameで指定したファイル名のデータを取得し、ct2を初期化する
        * `set_track_size(self, trackSize)`  
            trackSizeの変更
        * `get_data(self)`  
            マスク内の白い領域が最大の部分の  
            [重心x,　重心y, 左を起点とした横全体を1とする位置xの割合, 上を起点とした縦全体を1とする位置yの割合, 幅, 高さ, トラック領域の大きさ]  
            を取得する
        * `get_datas(self, num = 0)`  
            マスク内の白い領域を大きい順に、trackSize分のトラッキング結果を取得する
        * `save_color(self, fileName)`  
            指定色情報のファイルへの出力
    * `ct2`
        * `set_player_color(self, countTime = 5000)`  
            OpenCV依存のウィンドウを用いて色の動的指定を行う  
            取得した色のHSVの彩度と明度で閾値計算の処理分けを行うためのフラグを指定する
        * `player_color_range_judge(self)`
            1. 通常の閾値計算処理
            2. 明度が低い場合の閾値
            3. 彩度が低く明度が高い、白系の色の閾値  
            この三通りの他、HSV形式の色相が赤い場合に閾値の範囲が二つに分かれる処理を行う
            閾値をself.playerに代入する
        * `get_player_component(self)`  
            OpenCVのメソッドを用いてHSV画像のself.classFrameをself.playerの閾値で二値画像化を行う  
            その二値画像から、OpenCVのメソッドを用いてトラッキング処理結果を得る

* 静的関数
    * `set_capture_read()`  
        OpenCVのメソッドを用いてカメラから画像を取得し、ct2クラス変数に代入する
    * `set_camera_resolution(width, height)`  
        OpenCVのメソッドを用いてカメラの解像度を変更する

## 課題
* HSV変換時に黒色が赤色と同じ色相値をとるため、黒色が多量な状態での赤色のトラッキングが不安定
* 色を指定する際にある程度の操作をプレイヤーに強いてしまう
* トラッキング対象のHSVの閾値をプログラム実行中に補正していないため、カメラの調子による明度の変化に弱い