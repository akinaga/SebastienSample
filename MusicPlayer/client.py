#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame, json, sys, datetime, signal, base64
from websocket import create_connection

pygame.mixer.init()
user_id = open('user_id', 'r').read()

SERVER_ENDPOINT = "ws://hogehoge.com:4002/websocket"


def handler(signal, frame):
    ws.close()
    sys.exit(0)


def main():
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

        if msgs.get('name') == 'stop' and 'value' in msgs:
            pygame.mixer.music.stop()

        if msgs.get('name') == 'playback_audio' and 'value' in msgs:
            mp3data = base64.b64decode(msgs.get('value'))
            f = open("/dev/shm/temp.mp3", 'wb')
            f.write(mp3data)
            f.close()
            pygame.mixer.music.load("/dev/shm/temp.mp3")
            pygame.mixer.music.play(1)


if __name__ == "__main__":
    ws = create_connection(SERVER_ENDPOINT)
    pygame.init()
    main()
