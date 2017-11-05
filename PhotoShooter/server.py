#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)

from flask import request
from flask import make_response
import json
import base64
import photo

import gevent
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

# ポート番号
PORTNUMBER = 4000

# キューの初期化
orderitem = {}  # 処理受け渡しキューの初期化
talk = {}       # 会話内容のキュー


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST' and 'application/json' in request.headers.get('Content-Type', ""):
        event = request.json
        response = make_response()
        response.status_code = 200
        talk_json = request_handler(event, "")
        response.data = talk_json
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    else:
        return ""


@app.route('/websocket')
def websocket():
    global orderitem
    global talk

    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']

        message = ws.receive()
        client_info = json.loads(message)
        user_id = client_info.get('user_id')
        orderitem[user_id] = {}

        print "Connect : " + user_id

        while True:
            if user_id != "" and orderitem.get(user_id):
                ret = get_data(user_id, "photo")
                if ret != "":
                    # 写真撮影指示
                    ws.send(json.dumps({'user_id': user_id, 'name': "photo", 'value': ret}))

                    # 写真の受信待ち
                    img_json = ws.receive()

                    # 写真の受信処理
                    img_dic = json.loads(img_json)
                    img_txt = img_dic.get('img')
                    filename = img_dic.get('filename')
                    img = base64.b64decode(img_txt)
                    f = open(filename, 'wb')
                    f.write(img)
                    f.close()

                    # 写真の処理
                    result_json, sentense = photo.face_recognize(filename)
                    print result_json
                    print sentense
                    talk[user_id] = sentense

                    # 分析結果送信
                    ws.send(json.dumps({'user_id': user_id, 'name': "result", 'value': result_json}))

            gevent.sleep(0.3)


def put_data(user_id, queuename, value):
    global orderitem
    orderitem.update({user_id: {queuename: value}})


def get_data(user_id, queuename):
    global orderitem
    if orderitem.get(user_id):
        if orderitem[user_id].get(queuename):
            ret = orderitem[user_id].get(queuename)
            orderitem[user_id][queuename] = ""
            return ret
        else:
            return ""
    else:
        return ""


def request_handler(event, context):
    global talk
    intent = event["args"]["intent"]
    utterance = event["args"]["utterance"]
    user_id = event["user_id"]
    sentense = "良くわかりませんでした"

    if intent == "photo":
        print user_id, "photo"
        put_data(user_id, 'photo', "photo")
        while True:
            gevent.sleep(0.3)
            if talk.get(user_id):
                print "respose :", talk.get(user_id)
                break
        sentense = talk.get(user_id)
        del talk[user_id]

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

