# encoding: UTF-8

from flask import Flask
app = Flask(__name__)

from flask import request
from flask import make_response

import httplib
import urllib
import json
import os
import base64
from hashlib import md5
import gevent
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

# ポート番号の指定
PORTNUMBER = 4002

# 汎用キューの初期化
orderitem = {}

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST' and 'application/json' in request.headers.get('Content-Type', ""):
        event = request.json
        print event
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
        # flush_data(user_id)
        orderitem[user_id] = {}

        while True:
            if user_id != "" and orderitem.get(user_id):
                ret = get_data(user_id, "playback_audio")
                if ret != "":
                    ws.send(json.dumps({'user_id': user_id, 'name': "playback_audio", 'value': ret}))

                ret = get_data(user_id, "stop")
                if ret == "stop":
                    ws.send(json.dumps({'user_id': user_id, 'name': "stop", 'value': 'stop'}))

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

    if intent == "music":
        searchword = utterance[:utterance.find(u'の音楽')]
        mp3_txt = get_musicdata(searchword.encode("utf-8"))
        if mp3_txt == "":
            sentense = searchword.encode("utf-8") + "では何も見つかりませんでした。"
        else:
            put_data(user_id, 'playback_audio', mp3_txt)
            sentense = searchword.encode("utf-8") + "の音楽を再生します。"

    elif intent == "stop":
        put_data(user_id, 'stop', "")
        sentense = "音楽を停止しました"

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


def get_musicdata(searchword):
    uri_base = 'itunes.apple.com'
    # Request headers.
    headers = {
        'Content-Type': 'application/json',
    }

    # Request parameters.
    # searchword = "Perfume"
    params = urllib.urlencode({
        'term': searchword,
        'country': 'jp',
        'media': 'music',
        'limit': 1,
        'lang': 'ja_jp'
    })

    body = ""
    conn = httplib.HTTPSConnection(uri_base)
    conn.request("POST", "/search?%s" % params, body, headers)
    response = conn.getresponse()
    data = json.loads(response.read())
    mp3_txt = ""
    if data.get("results"):
        url = data["results"][0]["previewUrl"]

        mp3strage = "/dev/shm/"
        mp3filename = md5(url).hexdigest()

        tmp_filename = str(mp3filename) + ".m4a"
        filename = str(mp3filename) + ".mp3"

        if not os.path.exists(mp3strage + filename):
            urllib.urlretrieve(url, mp3strage + tmp_filename)
            os.system("/usr/local/bin/ffmpeg -i " + mp3strage + tmp_filename + ' -ab 192k -af "afade=t=in:ss=0:d=2,afade=t=out:st=28:d=2" ' + mp3strage + filename)
            mp3 = open(mp3strage + filename, 'rt').read()
            mp3_txt = base64.b64encode(mp3)

    return mp3_txt


if __name__ == "__main__":
    server = pywsgi.WSGIServer(('0.0.0.0', PORTNUMBER), app, handler_class=WebSocketHandler)
    server.serve_forever()

