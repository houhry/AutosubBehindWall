# -*- coding: utf-8 -*-
"""
Created on Sun Aug 06 05:26:49 2017
@author: alex
@contact wj3235@126.com
"""
import os
from aip import AipSpeech
from utility import write_txt_to_file
import http.client
import json
import hashlib
import urllib
import requests
import wave
import time
import base64
import random
#import azure.cognitiveservices.speech as speechsdk


def init_baidu():
    global B_APP_ID, B_API_KEY, B_SECRET_KEY
    B_APP_ID = '?'
    B_API_KEY = '?'
    B_SECRET_KEY = '?'

def baidu(filePath,samplerate,language):
    global B_APP_ID,B_API_KEY,B_SECRET_KEY
    aipSpeech = AipSpeech(B_APP_ID, B_API_KEY, B_SECRET_KEY)

    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()
        
    response=aipSpeech.asr(get_file_content(filePath), 'wav', samplerate, {
        'lan': language,
    })
    return response
        
def speech_recognizai_baidu(filepath,samplerate,language='zh'):
    return baidu2(filepath,samplerate,language)


def speech_recognizai_ali(filepath,samplerate,language='zh'):
    return A_process(A_request, A_token, filepath)

def speech_recognizai_tc(filepath,samplerate,language='zh'):
    return tencent(filepath)

def speech_recognizai_xf(filepath,samplerate,language='zh'):
    return xf(filepath)


def speech_recognizai_azure(filepath,samplerate,language='zh'):
    return azure2(filepath)


def baidu2(filestream,samplerate,language):
    global B_APP_ID,B_API_KEY,B_SECRET_KEY
    aipSpeech = AipSpeech(B_APP_ID, B_API_KEY, B_SECRET_KEY)
        
    response=aipSpeech.asr(filestream, 'wav', samplerate, {
        #'lan': language,
        'dev_pid': 1936,
    })
    return response

# -*- coding: UTF-8 -*-
# Python 2.x 引入httplib模块
# import httplib
# Python 3.x 引入http.client模块

def A_process(request, token, audioContent) :
    # 读取音频文件
    #with open(audioFile, mode = 'rb') as f:
    #    audioContent = f.read()
    host = 'nls-gateway.cn-shanghai.aliyuncs.com'
    # 设置HTTP请求头部
    httpHeaders = {
        'X-NLS-Token': token,
        'Content-type': 'application/octet-stream',
        'Content-Length': len(audioContent)
        }
    # Python 2.x 请使用httplib
    # conn = httplib.HTTPConnection(host)
    # Python 3.x 请使用http.client
    conn = http.client.HTTPConnection(host)
    conn.request(method='POST', url=request, body=audioContent, headers=httpHeaders)
    response = conn.getresponse()
    print('Response status and response reason:')
    print(response.status ,response.reason)
    body = response.read()
    try:
        print('Recognize response is:')
        body = json.loads(body)
        print(body)
        status = body['status']
        if status == 20000000 :
            #result = body['result']
            #print('Recognize result: ' + result)
            conn.close()
            return body
        else :
            print('Recognizer failed!')
    except ValueError:
        print('The response is not json format string')
    conn.close()


def init_ali():
    global A_appKey, A_token, A_url, A_request
    A_appKey = '?'
    A_token = '?'
    # 服务请求地址
    A_url = '?'
    # 音频文件
    #audioFile = '/path/to/nls-sample-16k.wav'
    A_format = 'pcm'
    A_sampleRate = 16000
    enablePunctuationPrediction  = True
    enableInverseTextNormalization = True
    enableVoiceDetection  = False
    # 设置RESTful请求参数
    A_request = A_url + '?appkey=' + A_appKey
    A_request = A_request + '&format=' + A_format
    A_request = A_request + '&sample_rate=' + str(A_sampleRate)
    if enablePunctuationPrediction :
        A_request = A_request + '&enable_punctuation_prediction=' + 'true'
    if enableInverseTextNormalization :
        A_request = A_request + '&enable_inverse_text_normalization=' + 'true'
    if enableVoiceDetection :
        A_request = A_request + '&enable_voice_detection=' + 'true'

def md5(string):
    md = hashlib.md5()
    md.update(string.encode('utf-8'))#python 3
    md5 = md.hexdigest().upper()
    return md5

def signify(args, app_key):
    query_str = urlencode(args)
    query_str = query_str + '&app_key=' + app_key
    signiture = md5(query_str)
    return signiture

def urlencode(args):
    tuples = [(k, args[k]) for k in sorted(args.keys()) if args[k]]
    #query_str = urllib.urlencode(tuples) #2.7??
    query_str = urllib.parse.urlencode(tuples) #python 3
    return query_str

def http_post(api_url, args):
    resp = requests.post(url=api_url, data=args)
    resp = json.loads(resp.text)
    return resp

#DingKe/yoyo
class BaseASR(object):
    ext2idx = {'pcm': '1', 'wav': '2', 'amr': '3', 'slk': '4'}

    def __init__(self, api_url, app_id, app_key):
        self.api_url = api_url
        self.app_id = app_id
        self.app_key = app_key

    def stt(self, audio_file, ext, rate):
        raise Exceptin("Unimplemented!")


class BasicASR(BaseASR):
    """ Online ASR from Tencent
    https://ai.qq.com/doc/aaiasr.shtml
    """
    def __init__(self, api_url='https://api.ai.qq.com/fcgi-bin/aai/aai_asr',
                 app_id='???', app_key='???'):
        super(BasicASR, self).__init__(api_url, app_id, app_key)

    def stt(self, audio_data, ext='wav', rate=16000):
        #if ext == 'wav':
        #    wf = wave.open(audio_file)
        #    nf = wf.getnframes()
        #    audio_data = wf.readframes(nf)
        #    wf.close()
       # else:
        #    raise Exception("Unsupport audio file format!")

        args = {
            'app_id': self.app_id,
            'time_stamp': str(int(time.time())),
            'nonce_str': '%.x' % random.randint(1048576, 104857600),
            'format': self.ext2idx[ext],
            'rate': str(rate),
            'speech': base64.b64encode(audio_data),
        }

        signiture = signify(args, self.app_key)
        args['sign'] = signiture
        resp = http_post(self.api_url, args)
        text = resp['data']['text'].encode('utf-8')

        DEBUG = 0 ##
        if DEBUG:
            print('msg: %s, ret: %s, format: %s' %
                  (resp['msg'], resp['ret'], resp['data']['format']))

        return resp


def init_tc():
    global asr_engine
    t_url = '?'
    t_appid = '?'
    t_key = '?'
    asr_engine = BasicASR(t_url, t_appid, t_key)


def tencent(audio_file):
    text = asr_engine.stt(audio_file)
    return text


def init_xf():
    global XF_key, XF_appid
    XF_appid = '?'
    XF_key = '?'


def xf(file_content):
    global XF_key, XF_appid
    # file_content 是二进制内容，bytes类型
    # 由于Python的字符串类型是str，在内存中以Unicode表示，一个字符对应若干个字节。
    # 如果要在网络上传输，或者保存到磁盘上，就需要把str变为以字节为单位的bytes
    # 以Unicode表示的str通过encode()方法可以编码为指定的bytes
    base64_audio = base64.b64encode(file_content)  # base64.b64encode()参数是bytes类型，返回也是bytes类型
    body = urllib.parse.urlencode({'audio': base64_audio})

    url = 'http://api.xfyun.cn/v1/service/v1/iat'
    api_key = XF_key
    param = {"engine_type": "sms16k", "aue": "raw"}

    x_appid = XF_appid
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))  # 改('''')
    # 这是3.x的用法，因为3.x中字符都为unicode编码，而b64encode函数的参数为byte类型，
    # 所以必须先转码为utf-8的bytes
    x_param = str(x_param, 'utf-8')

    x_time = int(int(round(time.time() * 1000)) / 1000)
    x_checksum = hashlib.md5((api_key + str(x_time) + x_param).encode('utf-8')).hexdigest()  # 改
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    # 不要忘记url = ??, data = ??, headers = ??, method = ?? 中的“ = ”，这是python3
    req = urllib.request.Request(url=url, data=body.encode('utf-8'), headers=x_header, method='POST')
    result = urllib.request.urlopen(req)
    result = result.read().decode('utf-8')
    print(result)
    result = json.loads(result)

    print(result)
    return result

#原文：https: // blog.csdn.net / Smile_coderrr / article / details / 81636015

def azure(audiowave):
    """performs one-shot speech recognition with input from an audio file"""
    # <SpeechRecognitionWithFile>
    speech_config = speechsdk.SpeechConfig(subscription='?', region='eastasia',
                                           speech_recognition_language="zh-CN")
    audio_config = speechsdk.audio.AudioConfig(stream=audiowave)
    # Creates a speech recognizer using a file as audio input.
    # The default language is "en-us".
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # Perform recognition. `recognize_once` blocks until an utterance has been recognized, after
    # which recognition stops and a result is returned.  Thus, it is suitable only for single shot
    # recognition like command or query.  For long-running recognition, use continuous recognitions
    # instead.
    result = speech_recognizer.recognize_once()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    # </SpeechRecognitionWithFile>

#https://www.taygan.co/blog/2018/02/09/getting-started-with-speech-to-text


YOUR_API_KEY = '?'
REGION = 'eastasia' # westus, eastasia, northeurope
MODE = 'Conversation'
LANG = 'zh-CN'
FORMAT = 'simple'

def azure2(input_audio):
    # 1. Get an Authorization Token
    token = get_token()
    print("token")
    print(token)
    # 2. Perform Speech Recognition
    results = get_text(token, input_audio)
    # 3. Print Results
    print(results)


def get_token():
    # Return an Authorization Token by making a HTTP POST request to Cognitive Services with a valid API key.
    url = 'https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken'
    headers = {
        'Ocp-Apim-Subscription-Key': YOUR_API_KEY
    }
    r = requests.post(url, headers=headers)
    token = r.content
    return token


def get_text(token, audio):
    # Request that the Bing Speech API convert the audio to text
    url = 'https://eastasia.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=zh-CN'
    headers = {
        'Accept': 'application/json',
        'Ocp-Apim-Subscription-Key': YOUR_API_KEY,
#        'Transfer-Encoding': 'chunked',
#        'Expect': '100-continue',
        'Content-type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
        'Authorization': 'Bearer {0}'.format(token)
    }
    r = requests.post(url, headers=headers, data=audio)
    results = json.loads(r.content)
    return results

