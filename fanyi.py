#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A simple translation tool with text-to-speech support"""

import subprocess
import random
import hashlib
from urllib import parse, request
import json
import shelve
import datetime
import os
import argparse
from concurrent import futures

# api key for baidu fanyi
FY_APPID = 'your baidu fanyi app id'
FY_APIKEY = 'your baidu fanyi api key'
FY_BASE_URL = 'https://api.fanyi.baidu.com/api/trans/vip/translate'

# api key for baidu yuyin
YY_APPKEY = 'your baidu yuyin app key'
YY_SECRETKEY = 'your baidu yuyin secret key'
YY_TOKEN_URL = 'https://openapi.baidu.com/oauth/2.0/token'
YY_BASE_URL = 'https://tsn.baidu.com/text2audio'


def checkout(cmd: list) -> str:
    """Run command with arguments and return the result."""
    try:
        completed = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return 'ERR'
    else:
        return completed.stdout.decode('utf-8')


def get_token() -> str:
    """Return the valid Baidu Yuyin access token."""
    with shelve.open('token.db', writeback=True) as t:
        if all(k in t for k in ['token', 'expire_time']) and (t['expire_time'] > datetime.datetime.now()):
            return t['token']
        else:
            query_args = {
                'grant_type': 'client_credentials',
                'client_id': YY_APPKEY,
                'client_secret': YY_SECRETKEY
            }
            encoded_args = parse.urlencode(query_args)
            res = json.loads(request.urlopen(YY_TOKEN_URL + '?' + encoded_args).read())
            t['token'] = res['access_token']
            t['expire_time'] = datetime.datetime.now() + datetime.timedelta(seconds=res['expires_in'] - 3600)
            return res['access_token']


def translate(words: str):
    """Translate the word."""
    salt = random.randint(32768, 65536)
    sign_str = FY_APPID + words + str(salt) + FY_APIKEY
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    query_args = {
        'q': words,
        'from': 'auto',
        'to': 'zh',
        'appid': FY_APPID,
        'salt': salt,
        'sign': sign
    }
    encoded_args = parse.urlencode(query_args)
    res = json.loads(request.urlopen(FY_BASE_URL, encoded_args.encode('utf-8')).read())
    checkout(['notify-send', words, res['trans_result'][0]['dst']])


def pronounce(words: str):
    """Pronounce the word."""
    token = get_token()
    cuid = os.uname().nodename
    query_args = {
        'tex': words,
        'tok': token,
        'cuid': cuid,
        'ctp': 1,
        'lan': 'zh'
    }
    encoded_args = parse.urlencode(query_args)
    checkout(['mpv', '--quiet', YY_BASE_URL + '?' + encoded_args])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('words', nargs='?', default=checkout(['xsel', '-o']))
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()
    with futures.ThreadPoolExecutor(max_workers=2) as e:
        e.submit(translate, args.words)
        if not args.quiet:
            e.submit(pronounce, args.words)


if __name__ == '__main__':
    main()
