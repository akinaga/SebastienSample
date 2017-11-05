#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import json


def face_recognize(filename):
    subscription_key = "******************************"
    uri_base = 'southeastasia.api.cognitive.microsoft.com'
    # Request headers.
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': subscription_key,
    }

    # Request parameters.
    params = urllib.urlencode({
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender',
    })
    result = []
    try:
        # Execute the REST API call and get the response.
        conn = httplib.HTTPSConnection(uri_base)
        conn.request("POST", "/face/v1.0/detect?%s" % params, open(filename, 'rb'), headers)
        response = conn.getresponse()
        data = response.read()

        # 'data' contains the JSON data. The following formats the JSON data for display.
        result = json.loads(data)
        conn.close()

    except Exception as e:
        pass

    print result

    result_txt = ""
    for result_p in result:
        if result_txt != "":
            result_txt += "|"
        result_txt += str(result_p['faceAttributes']['gender']) + "," + str(result_p['faceAttributes']['age'])
    if result_txt == "":
        result_txt = "none"

    return json.dumps(result), make_response_how_old(result_txt)


def make_response_how_old(msg):
    nothing = False
    people = []
    if msg == "none" or msg == "":
        nothing = True
        speech_output = "どなたも僕の前には居ないように見えます。"
    else:
        people = msg.split("|")

    if len(people) >= 1 and nothing == False:
        speech_output = "私には" + count_people(people) + "見えています. "
        if len(people) > 5:
            max = 0
            min = 999
            for i in people:
                if max < int(float(i.split(",")[1])):
                    max = int(float(i.split(",")[1]))
                if min > int(float(i.split(",")[1])):
                    min = int(float(i.split(",")[1]))
            speech_output += "大勢いらっしゃいますが、" + str(min) + "歳から" + str(max) + "歳までの方がいらっしゃるよう"
        elif len(people) > 1:
            speech_output += "それぞれ、"
            for i in people:
                speech_output += str(int(float(i.split(",")[1]))) + "歳,"
        else:
            for i in people:
                speech_output += str(int(float(i.split(",")[1]))) + "歳"
        speech_output += "に見えました。いかがでしょうか？"
    else:
        speech_output = "どなたも僕の前には居ないように見えます。"

    return speech_output


def count_people(people):
    Male = 0
    Female = 0
    for i in people:
        print i
        if i.split(",")[0] == "male":
            Male += 1
        elif i.split(",")[0] == "female":
            Female += 1
    msg = ""
    if Male > 0:
        msg += "男性が" + str(Male) + "名"
    if Female > 0:
        msg += "女性が" + str(Female) + "名"

    return msg