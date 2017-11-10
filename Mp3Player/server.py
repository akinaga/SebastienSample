# encoding: UTF-8

from flask import Flask
app = Flask(__name__)

from flask import request
from flask import make_response

import json
import gevent
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import base64

PORTNUMBER = 4001

# 汎用キューの初期化
orderitem = {}


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST' and 'application/json' in request.headers.get('Content-Type', ""):
        event = request.json
        response = make_response()
        response.status_code = 200
        response.data = request_handler(event, "")
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    else:
        return ""


@app.route('/websocket')
def websocket():
    global orderitem
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']

        message = ws.receive()
        client_info = json.loads(message)
        user_id = client_info.get('user_id')
        orderitem[user_id] = {}
        print client_info

        while True:
            if user_id != "" and orderitem.get(user_id):
                ret = get_data(user_id, "playback_audio")
                if ret != "":
                    # ローカルの音楽を再生
                    ws.send(json.dumps({'user_id': user_id, 'name': "play_mp3", 'value': ret}))

                    # リモートの音楽を作成
                    # ws.send(json.dumps({'user_id': user_id, 'name': "play_download", 'value': ret}))

            gevent.sleep(0.3)


def put_data(user_id, queuename, value):
    global orderitem
    orderitem.update({user_id: {queuename: value}})


def get_data(user_id, queuename):
    global orderitem
    if orderitem.get(user_id):
        if orderitem[user_id].get(queuename):
            ret = orderitem[user_id].get(queuename)
            del orderitem[user_id][queuename]
            return ret
        else:
            return ""
    else:
        return ""


def request_handler(event, context):
    intent = event["args"]["intent"]
    utterance = event["args"]["utterance"]
    user_id = event["user_id"]

    print intent

    if intent == "playmp3":
        # MP3のファイルをここで指定
        put_data(user_id, 'playback_audio', "potato.mp3")

        # リモートのMP3を送信する場合はこちら
        # mp3 = open('potato.mp3', 'rt').read()
        # mp3_txt = base64.b64encode(mp3)
        # put_data(user_id, 'playback_audio', mp3_txt)

        # 話す内容はここに記載。ただし、音とは同期しない
        sentense = "ポテトが出来ました"
    else:
        # それ以外は無音応答
        sentense = ""

    print sentense

    return json.dumps(
        {"error_code": "success",
         "status": "true",
         "user_id": event["user_id"],
         "bot_id": event["bot_id"],
         "params": {"status": "true",
                    "message": sentense
                    }
         }
    )


if __name__ == "__main__":
    server = pywsgi.WSGIServer(('0.0.0.0', PORTNUMBER), app, handler_class=WebSocketHandler)
    server.serve_forever()

