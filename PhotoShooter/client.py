#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame, json, sys, urllib, datetime, signal
from websocket import create_connection
import uuid
import picamera
import os
import base64


pygame.mixer.init()

if os.path.exists('user_id'):
    user_id = open('user_id', 'r').read()
else:
    user_id = "test001"

SERVERNAME = "hogehoge.com:4000"
SERVER_ENDPOINT = "ws://" + SERVERNAME + "/websocket"
ws = create_connection(SERVER_ENDPOINT)


def handler(signal, frame):
    ws.close()
    sys.exit(0)


def takePicture():
    filename = str(uuid.uuid4()) + ".jpg"
    r = capture_pi_camera('/dev/shm/' + filename)

    background = pygame.image.load('/dev/shm/' + filename).convert()
    screen.blit(background, (80, 0))
    pygame.display.update()
    return filename


def capture_pi_camera(filename):
    with picamera.PiCamera() as camera:
        # camera.resolution = (1024, 768)
        camera.resolution = (640, 480)
        camera.rotation = 180
        camera.capture(filename)
    if os.path.exists(filename):
        return True
    else:
        return False


def main():
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

        if msgs.get('name') == 'photo' and 'value' in msgs:

            # 写真を撮る処理とか
            filename = takePicture()

            # 写真の送信
            img = open('/dev/shm/' + filename, 'rt').read()
            img_txt = base64.b64encode(img)
            ws.send(json.dumps({'filename': filename, "img": img_txt}, indent=2))


if __name__ == "__main__":
    pygame.init()
    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    print "Framebuffer size: %d x %d" % (size[0], size[1])
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    # screen = pygame.display.set_mode(size)

    # keifont = pygame.font.Font("/usr/share/fonts/truetype/kochi/kochi-gothic.ttf", 80)
    # title = keifont.render(u"なかよしデジカメ", True, (255,255,255))
    pygame.mouse.set_visible(False)
    screen.fill((0, 0, 0))
    main()
