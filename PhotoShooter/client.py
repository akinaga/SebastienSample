#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame, json, sys, urllib2, datetime, signal
from websocket import create_connection
import uuid
import picamera
import os
import base64
import numpy as np
import cv2

pygame.mixer.init()

SERVER_ENDPOINT = "ws://hogehoge.com:4000/websocket"
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


def make_connection():
    # コネクション作成
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

            # 解析結果の受信
            message = ws.recv()
            msgs = json.loads(message)
            if msgs.get('name') == 'result' and 'value' in msgs:
                result = json.loads(msgs.get('value'))
                if len(result) != 0:

                    # Load the original image from disk
                    # Convert string to an unsigned int array
                    data8uint = np.fromstring(open('/dev/shm/' + filename, 'rb').read(), np.uint8)
                    img = cv2.imdecode(data8uint, cv2.IMREAD_COLOR)
                    renderResultOnImage(result, img)
                    cv2.imwrite('/dev/shm/' + filename + ".added.jpg", img)
                    background = pygame.image.load('/dev/shm/' + filename + ".added.jpg").convert()
                    screen.blit(background, (80, 0))
                    pygame.display.update()
                    os.remove('/dev/shm/' + filename + ".added.jpg")
            os.remove('/dev/shm/' + filename)


# 画像に結果をオーバレイ
def renderResultOnImage(result, img):
    # Display the obtained results onto the input image
    for currFace in result:
        faceRectangle = currFace['faceRectangle']
        cv2.rectangle(img,(faceRectangle['left'],faceRectangle['top']),
                           (faceRectangle['left']+faceRectangle['width'], faceRectangle['top'] + faceRectangle['height']),
                       color=(255,0,0), thickness=1)

    for currFace in result:
        faceRectangle = currFace['faceRectangle']
        faceAttributes = currFace['faceAttributes']

        textToWrite = "%c (%d)" % ( 'M' if faceAttributes['gender']=='male' else 'F', faceAttributes['age'] )
        cv2.putText( img, textToWrite, (faceRectangle['left'],faceRectangle['top']-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1 )


if __name__ == "__main__":
    # ユーザID取得
    if os.path.exists('config.json'):
        device_token = json.loads(open('config.json', 'r').read()).get("AccessToken")
        if not device_token:
            raise Exception("config.jsonファイルが不正です")
    else:
        raise Exception("Device Tokenファイルが見つかりませんでした。device_tokenファイルを同じフォルダに置いて下さい。")

    print "https://users.sebastien.ai/api/validate_device_token?device_token=" + device_token
    result = urllib2.urlopen('https://users.sebastien.ai/api/validate_device_token?device_token=' + device_token).read()
    user_id = json.loads(result).get('shadow_id')

    # 画面初期化
    pygame.init()
    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    print "Framebuffer size: %d x %d" % (size[0], size[1])
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

    pygame.mouse.set_visible(False)
    screen.fill((0, 0, 0))

    # サーバーへ接続
    make_connection()
