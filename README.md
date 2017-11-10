# Sebastien Code Samples
These are sample codes of DOCOMO AI Agent (Sebastien)

## Description
このコードはドコモAIエージェントのエキスパートエージェントのサンプルコードです。エキスパートエージェントをRaspberryPi上に実装し、
さらにclient.pyを走行させることで、server.pyと連携し、下記のデモを実現できます。
1. 写真を撮ってと言われると画像を伝送するデモ(PhotoShooter)
- RaspberryPiで画像を撮影し、Websocketで転送することで、サーバーに画像を伝送します。
- 転送された画像はMicrosoftのFaceAPIによって年齢を推定します。推定結果を音声で返します。
2. インテントに応じて音を鳴らすデモ(Mp3Player)
- RaspberryPi上でMp3を鳴らします。インテントに応じて、予め設定されているMp3を鳴らしたり、サーバ上のMp3ファイルを転送して鳴らすことが出来ます。
3. 好きな音楽を鳴らすデモ(MusicPlayer)
- iTunesから音楽を検索して、RaspberryPi上で鳴らすことが出来るデモです。

## Usage
いずれのコードも2つのコンポーネント(クライアントとサーバー)から出来ています。
Websocketベースですので、サーバーが別途必要です。WebSocketなので、サーバーレスには出来ません。

|対象|説明|
|---|---|
|クライアント|クライアントのソフトウェアです(client.py)。Raspberry Pi上で動作させます。起動と同時にWebSocketをServerに対して張り、命令を待ちます。|
|サーバー|サーバー側に配置します(server.py)。PythonのFlaskで実装しています。EC2などのサーバー上に配置して利用下さい。|
|基盤上の設定|[Developer Console](https://developers.sebastien.ai/)上でインテントの設定をして下さい。例１〜３での必要なインテントは異なります。|

### インテントの設定方法
下記の例ではMp3Playerのインテントの設定例です。
![インテント設定例](img/ddb_sample.png)

-------
## PhotoShooter
### シーケンス図
![Sanmple1](img/sample1.png)

### 利用上の注意
- サーバーのエンドポイントの設定はハードコートしていますので、適宜変更下さい。
- マイクロソフトのFaceAPIのCredentialはハードコートしていますので、適宜変更下さい。

### 必要なインテント
|photo|写真撮影指示を駆動するためのインテントです。『写真お願い』『何歳に見える』等で設定してください。|
|---|---|

## Mp3Player
### シーケンス図
![Sanmple1](img/sample2.png)

### 利用上の注意
- サーバーのエンドポイントの設定はハードコートしていますので、適宜変更下さい。

### 必要なインテント
|playmp3|音を鳴らすための駆動インテントです。『ポテトお願い』でポテト音を駆動します。|
|---|---|

## MusicPlayer
### シーケンス図
![Sanmple1](img/sample3.png)

### 利用上の注意
- サーバーのエンドポイントの設定はハードコートしていますので、適宜変更下さい。

### 必要なインテント
|music|音楽の再生を促すインテントです。『＊の音楽＊』などで呼び出すと、〜の音楽の『〜』の部分を検索語として音楽を検索します。|
|---|---|

## Licence

再配布、改変自由です。

## Author

[akinaga](https://github.com/akinaga)
