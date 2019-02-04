# -*- coding:utf-8 -*-
import certifi
import pycurl
import requests
import os
import json
import uuid
from StringIO import StringIO


def byteify(input_data):
    # convert json to list
    if isinstance(input_data, dict):
        return {byteify(key): byteify(value) for key, value in input_data.iteritems()}
    elif isinstance(input_data, list):
        return [byteify(element) for element in input_data]
    elif isinstance(input_data, unicode):
        return input_data.encode('utf-8')
    else:
        return input_data


def read_in_chunks(file_object, chunk_size=1024):
    # post chunk encoding data
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


class Authentication:
    # get token
    def __init__(self, client_id, client_secret):
        self.AccessUrl = "https://oxford-speech.cloudapp.net/token/issueToken"
        self._clientId = client_id
        # provided by MS
        self._clientSecret = client_secret
        # provided by MS
        self.request_data = 'grant_type=client_credentials&client_id=' + self._clientId+'&client_secret='
        self.request_data += self._clientSecret + '&scope=https://speech.platform.bing.com'
        # opt must be a string object not a unicode object
        data_l = len(self.request_data)
        http_header = [
                       "Content-Type:application/x-www-form-urlencoded"
                       ]

        storage = StringIO()
        # the way to get response and print it
        c = pycurl.Curl()
        c.setopt(pycurl.CAINFO, certifi.old_where())
        c.setopt(pycurl.URL, self.AccessUrl)
        c.setopt(c.HTTPHEADER, http_header)
        c.setopt(c.POST, 1)
        c.setopt(c.POSTFIELDSIZE, data_l)
        c.setopt(c.CONNECTTIMEOUT, 30)
        c.setopt(c.TIMEOUT, 30)
        c.setopt(c.POSTFIELDS, self.request_data)
        # --------------------------------------------
        c.setopt(c.WRITEFUNCTION, storage.write)
        # --------------------------------------------
        c.perform()
        c.close()
        body = storage.getvalue()
        storage.close()
        self._token = byteify(json.loads(body.decode()))

    def getAccessToken(self):
        return self._token["access_token"]


class MsSpeechRequest:
    def __init__(self, audiofile, audioSamplerate=16000, clientid='', clientsecret='', locale='zh-CN', deviceOS='Rasbian'):
        if audiofile == None:
            print 'audio input wrong'
            return
        try:
            self._auth = Authentication(clientid, clientsecret)
        except Exception as e:
            print 'failed get access token.details:%s',e.__str__()
        self._RequestUri = "https://speech.platform.bing.com/recognize"
        self._RequestUri += "?scenarios=smd"
        self._RequestUri += "&appid="
        # input appid
        self._RequestUri += "&locale="+locale
        self._RequestUri += "&device.os="+deviceOS
        self._RequestUri += "&version=3.0"
        self._RequestUri += "&format=json"
        self._RequestUri += "&instanceid="
        # input instance id
        self._RequestUri += "&requestid="+str(uuid.uuid4())
        self._audioFile = audiofile
        self._audioSamplerate = audioSamplerate.__str__()
        self._token = self._auth.getAccessToken()
        # print self._token
        self._response = ''

    def post_request(self):
        headers = {}
        headers['Accept'] = 'application/json;text/xml'
        headers['Content-Type'] = 'audio/wav; codec=\"audio/pcm\"; samplerate='+self._audioSamplerate
        headers['Authorization'] = 'Bearer '+'%s' % self._token
        try:
            with open(self._audioFile,'rb') as f:
                r=requests.post(self._RequestUri, data=read_in_chunks(f), headers=headers, stream=True)
                print r
                self._response = byteify(r.text)
                print self._response
        except Exception as e:
            print 'failed get request response. Details:%s',e.__str__()

    def returnResult(self):
        self.post_request()
        return self._response
#---------------------
#作者：艾木的星辰
#来源：CSDN
#原文：https://blog.csdn.net/joyjun_1/article/details/52563713
#版权声明：本文为博主原创文章，转载请附上博文链接！