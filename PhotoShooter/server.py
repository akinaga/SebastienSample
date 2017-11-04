#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)

from flask import request
from flask import make_response

import json
import gevent
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

import base64

PORTNUMBER = 4000

# 汎用キューの初期化
orderitem = {}

# 話す内容のキュー
talk = ""


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST' and 'application/json' in request.headers.get('Content-Type', ""):
        event = request.json
        print event
        response = make_response()
        response.status_code = 200
        talk_json = request_handler(event, "")
        response.data = talk_json
        print talk_json
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
                    ws.send(json.dumps({'user_id': user_id, 'name': "photo", 'value': ret}))
                    img_json = ws.receive()
                    # 受けとったあとの処理
                    img_dic = json.loads(img_json)
                    img_txt = img_dic.get('img')
                    filename = img_dic.get('filename')
                    img = base64.b64decode(img_txt)
                    f = open(filename, 'wb')
                    f.write(img)
                    f.close()

                    talk = "写真を撮ったよ"

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
    # user_id = event["user_id"]
    user_id = "test001"
    sentense = "良くわかりませんでした"

    if intent == "photo":
        print user_id, "photo"
        put_data(user_id, 'photo', "photo")
        while True:
            gevent.sleep(0.3)
            if talk != "":
                print "respose :", talk
                break
        sentense = talk
        talk = ""

        print "sentense :", sentense

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

