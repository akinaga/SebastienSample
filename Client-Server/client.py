#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame, json, sys, urllib, datetime, signal
from websocket import create_connection

pygame.mixer.init()
user_id = open('user_id', 'r').read()

SERVER_ENDPOINT = "https://hogeserver.com/hoge"
FILESERVER = "https://hogehoge.com/"
ws = create_connection(SERVER_ENDPOINT)


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

        if msgs.get('name') == 'playback_audio' and 'value' in msgs:
            filename = msgs.get('value')
            urllib.urlretrieve(FILESERVER + filename, '/dev/shm/' + filename)
            pygame.mixer.music.load("/dev/shm/" + filename)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(1)


if __name__ == "__main__":
    main()
