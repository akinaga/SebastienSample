#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame, json, sys, datetime, signal, urllib2, os
from websocket import create_connection
import base64

# サーバーのエンドポイント
SERVER_ENDPOINT = "ws://hogehoge.com:4001/websocket"


def handler(signal, frame):
    ws.close()
    sys.exit(0)


def main():
    pygame.init()

    ws = create_connection(SERVER_ENDPOINT)
    items = {
        "user_id": user_id,
        "name": "init",
        "value": user_id,
        "time": datetime.datetime.now().isoformat()
    }
    ws.send(json.dumps(items, indent=2))
    signal.signal(signal.SIGINT, handler)

    while 1:
        message = ws.recv()
        msgs = json.loads(message)

        if msgs.get('name') == 'play_mp3' and 'value' in msgs:
            filename = msgs.get('value')
            pygame.mixer.music.load(filename)
        elif msgs.get('name') == 'play_download' and 'value' in msgs:
            mp3data = base64.b64decode(msgs.get('value'))
            f = open("/dev/shm/temp.mp3", 'wb')
            f.write(mp3data)
            f.close()
            pygame.mixer.music.load("/dev/shm/temp.mp3")
        pygame.mixer.music.play(1)


if __name__ == "__main__":

    pygame.mixer.init()
    ws = create_connection(SERVER_ENDPOINT)

    # ユーザID取得
    if os.path.exists('config.json'):
        device_token = json.loads(open('config.json', 'r').read()).get("AccessToken")
        if not device_token:
            raise Exception("config.jsonファイルが不正です")
    else:
        raise Exception("Device Tokenファイルが見つかりませんでした。device_tokenファイルを同じフォルダに置いて下さい。")

    result = urllib2.urlopen('https://users.sebastien.ai/api/validate_device_token?device_token=' + device_token).read()
    user_id = json.loads(result).get('shadow_id')

    main()
