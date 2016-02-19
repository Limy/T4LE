#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import urllib
import datetime
import subprocess
import random
import md5

# api key, six million per month
APPID = 'You baidu translate appid'
APIKEY = 'You baidu translate apikey'
PATH = '~/vocabulary' # make sure the path exist
FILENAME = os.path.join(os.path.expanduser(PATH), str(datetime.date.today()) + '.txt')

def main():
    word = subprocess.check_output('xsel')
    salt = random.randint(32768, 65536)
    sign = APPID +  word + str(salt) + APIKEY
    m1 = md5.new()
    m1.update(sign)
    sign = m1.hexdigest()
    params = urllib.urlencode({'q': word, 'from': 'auto', 'to': 'zh', 'appid':APPID, 'salt': salt, 'sign': sign})
    f = urllib.urlopen("http://api.fanyi.baidu.com/api/trans/vip/translate?%s", params)
    j = json.loads(f.read())
    d = dict(j['trans_result'][0])
    subprocess.call(['notify-send', word, d['dst']])

    with open(FILENAME, 'a+', 0) as f:
        f.write(word + '\n')

if __name__ == '__main__':
    main()
