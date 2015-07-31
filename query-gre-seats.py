#!/usr/bin/python -tt
# Copyright 2013 yipeipei@gmail.com

# Query GRE Seats
# https://github.com/yipeipei/query-gre-seats

"""
This script needs a runtime of Python 2.7.3
A simple script automatic query the GRE seats info from NEEA.
"""

import sys
import os
import time
import json
import winsound
from configparser import ConfigParser
from urllib.request import HTTPCookieProcessor, HTTPHandler, build_opener
from http.cookiejar import CookieJar
from urllib.parse import quote, urlencode

__version__ = '1.1'
__ring__ = 'ring.wav'

__config__ = 'config.ini'
DEBUG = 'debug.ini'

if os.path.exists(DEBUG):
    __config__ = DEBUG

WIDTH = 80
HEIGHT = 40
ISOTIMEFORMAT = '%Y-%m-%d %X'

LOGIN_PAGE = 'login.do?lang=CN'
QUERY_PAGE = 'testSites.do?'
PARA = {'p': 'testSites', 'm': 'ajax', 'ym': '', 'neeaID': '', 'cities': '', 'citiesNames': '', 'whichFirst': 'AS',
        'isFilter': 0, 'isSearch': 1}
QUERY_LIST = []
IS_LOGIN = False
WATCH_FLAG = False

POST_DATA = {'neeaID': '', 'pwd': ''}

CJ = CookieJar()
opener = build_opener(HTTPCookieProcessor(CJ), HTTPHandler)


class Common(object):
    """global config object"""

    def __init__(self):
        """load config from __config__"""
        self.CONFIG = ConfigParser()
        self.CONFIG.read(os.path.join(os.getcwd(), __config__))

        self.USERINFO_NEEAID = self.CONFIG.getint('user', 'neea_id')
        self.USERINFO_PWD = self.CONFIG.get('user', 'password')
        self.USERINFO_URL = self.CONFIG.get('user', 'url')

        self.QUERY_INTERVAL = self.CONFIG.getfloat('query', 'time_interval')
        self.QUERY_YEAR = self.CONFIG.get('query', 'year')
        self.QUERY_MONTH = self.CONFIG.get('query', 'month').split('|')
        self.QUERY_CITYCN = self.CONFIG.get('query', 'city_cn').split('|')
        self.QUERY_CITYEN = self.CONFIG.get('query', 'city_en').split('|')

        self.QUERY_WATCH = self.CONFIG.get('query', 'watch').split('|')

    def do_login(self):
        global IS_LOGIN
        global LOGIN_PAGE
        LOGIN_PAGE = self.USERINFO_URL + LOGIN_PAGE

        POST_DATA['neeaID'] = self.USERINFO_NEEAID
        POST_DATA['pwd'] = self.USERINFO_PWD

        post_data_urlencode = urlencode(POST_DATA)
        post_data_encode = post_data_urlencode.encode(encoding='utf-8', errors='strict')

        opener.open(LOGIN_PAGE, post_data_encode)
        IS_LOGIN = True

    def gen_query(self):
        global QUERY_LIST
        PARA['neeaID'] = self.USERINFO_NEEAID
        PARA['cities'] = ';'.join(self.QUERY_CITYEN) + ';'
        PARA['citiesNames'] = ';'.join(self.QUERY_CITYCN) + ';'
        for mon in self.QUERY_MONTH:
            ym = str(self.QUERY_YEAR) + '-' + str(mon)
            PARA['ym'] = ym
            query = urlencode(PARA)
            query = self.USERINFO_URL + QUERY_PAGE + query
            QUERY_LIST.append(query)


common = Common()


def watch(site):
    global WATCH_FLAG
    for it in common.QUERY_WATCH:
        it = it.split('@')

        if site['bjtime'].find(it[0], 'utf-8') != -1 and site['siteName'].find(it[1], 'utf-8') != -1:
            print('^O^' * 3, site['bjtime'], end='')
            WATCH_FLAG = True


def print_sites(data):
    for site in data:
        # for key, value in site.items():
        #     print value,'\t',
        # print '\n'
        if site['isClosed'] == 1:
            print('closed ', end='')
        else:
            if site['realSeats'] == 1:
                print('-> ^O^ ', end='')
                watch(site)
            else:
                print('  full ', end='')

        print(site['siteCode'], end='')
        print(site['siteName'])


def print_dates(data):
    for date in data:
        print(date['bjTime'])
        print_sites(date['sites'])
        print('')


def print_json(data):
    print('-' * (WIDTH - 10))
    print('\t\t\trefreshed at', time.strftime(ISOTIMEFORMAT, time.localtime(time.time())))
    for city in data:
        # print city['city']
        print_dates(city['dates'])


def start_query():
    global IS_LOGIN

    if not IS_LOGIN:
        common.do_login()

    show_info()

    for query in QUERY_LIST:
        echo = opener.open(query).read().decode('utf-8')
        data = json.loads(echo)
        if type(data) is dict:
            IS_LOGIN = False
            return
        print_json(data)


def show_info():
    info = '\n' * HEIGHT
    info += '------------------------query GRE Seats------------------------------\n'
    info += 'Version     :%s (Python %s)\n' % (__version__, sys.version.partition(' ')[0])
    info += 'Query Site  :%s\n' % common.USERINFO_URL
    info += 'Query Month :%s\n' % '|'.join(common.QUERY_MONTH)
    info += 'Query City  :%s\n' % '|'.join(common.QUERY_CITYCN)
    info += 'Watch       :%s\n' % '|'.join(common.QUERY_WATCH)
    info += 'Contact     :%s' % 'yipeipei@gmail.com'
    print(info)


def main():
    # sys.setdefaultencoding('utf-8')
    common.gen_query()
    # echo = opener.open(QUERY_LIST[0]).read().decode('utf-8')
    # print echo
    while True:
        start_query()
        # print WATCH_FLAG
        if WATCH_FLAG:
            while True:
                winsound.PlaySound(os.path.join(os.getcwd(), __ring__), winsound.SND_LOOP & winsound.SND_NOSTOP)
        else:
            time.sleep(common.QUERY_INTERVAL)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
