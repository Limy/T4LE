#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import json
import urllib
import subprocess

# api key, 1000 times per hour
APIKEY = 'WGCxN9fzvCxPo0nqlzGLCPUc'

def main():
    word = subprocess.check_output('xsel')
    params = urllib.urlencode({'from': 'auto', 'to': 'auto', 'client_id':APIKEY, 'q': word})
    f = urllib.urlopen("http://openapi.baidu.com/public/2.0/bmt/translate?%s", params)
    j = json.loads(f.read())
    d = dict(j['trans_result'][0])
    subprocess.call(['notify-send', word, d['dst']])

if __name__ == '__main__':
    main()