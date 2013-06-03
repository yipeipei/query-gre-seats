#!/usr/bin/python -tt
# Copyright 2013 yipeipei@gmail.com

# Query GRE Seats
# https://github.com/yipeipei/query-gre-seats

'''
This script needs a runtime of Python 2.7.3
A simple script automatic query the GRE seats info from NEEA.
'''

import sys
import os
import re
import ConfigParser
import urllib
import urllib2
import cookielib
import json
import time
import winsound
import types

__version__ = '1.1'
__ring__ = 'ring.wav'

__config__ = 'config.ini'
DEBUG = 'config.ini.debug'

# if DEBUG exists, run with debug profile
if os.path.exists(DEBUG):
    __config__ = DEBUG

WIDTH = 80
HEIGHT = 40
ISOTIMEFORMAT = '%Y-%m-%d %X'

LOGIN_PAGE = 'login.do?lang=CN'
QUERY_PAGE = 'testSites.do?'
PARA = {'p':'testSites', 'm':'ajax', 'ym':'', 'neeaID':'', 'cities':'', 'citiesNames':'', 'whichFirst':'AS', 'isFilter':0, 'isSearch':1}
QUERY_LIST = []
IS_LOGIN = False
WATCH_FLAG = False

# HEADER = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.X.Y.Z Safari/525.13.'), ]
POST_DATA = {'submit':'', 'neeaID':'', 'pwd':''}

# global var
CJ = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CJ), urllib2.HTTPHandler)
# opener.addheaders = HEADER

class Common(object):
    '''global config object'''

    def __init__(self):
        '''load config from __config__'''
        ConfigParser.RawConfigParser.OPTCRE = re.compile(r'(?P<option>[^=\s][^=]*)\s*(?P<vi>[=])\s*(?P<value>.*)$')
        self.CONFIG = ConfigParser.ConfigParser()
        self.CONFIG.read(os.path.join(os.getcwd(), __config__))

        self.USERINFO_NEEAID = self.CONFIG.getint('user', 'neea_id')
        self.USERINFO_PWD = self.CONFIG.get('user', 'password')
        self.USERINFO_URL = self.CONFIG.get('user', 'url')

        self.QUERY_INTERVAL = self.CONFIG.getfloat('query','time_interval')
        self.QUERY_YEAR = self.CONFIG.get('query', 'year')
        self.QUERY_MONTH = self.CONFIG.get('query', 'month').split('|')
        self.QUERY_CITYCN = self.CONFIG.get('query', 'city_cn').split('|')
        self.QUERY_CITYEN = self.CONFIG.get('query', 'city_en').split('|')
        
        self.QUERY_WATCH = self.CONFIG.get('query', 'watch').split('|')
    
    def doLogin(self):
        global IS_LOGIN
        global LOGIN_PAGE
        LOGIN_PAGE = self.USERINFO_URL + LOGIN_PAGE
        
        POST_DATA['neeaID'] = self.USERINFO_NEEAID
        POST_DATA['pwd'] = self.USERINFO_PWD
        
        post_data_urlencode = urllib.urlencode(POST_DATA)
        post_data_encode = post_data_urlencode.encode(encoding='utf-8', errors='strict')
    
        login_r = opener.open(LOGIN_PAGE, post_data_encode)
        IS_LOGIN = True
        
    def genQuery(self):
        global QUERY_LIST
        PARA['neeaID'] = self.USERINFO_NEEAID
        PARA['cities'] = ';'.join(self.QUERY_CITYEN)+';'
        PARA['citiesNames'] = ';'.join(self.QUERY_CITYCN)+';'
        for mon in self.QUERY_MONTH:
            ym = str(self.QUERY_YEAR) + '-' + str(mon)
            PARA['ym'] = ym 
            query = urllib.urlencode(PARA)
            query = self.USERINFO_URL + QUERY_PAGE + query
            QUERY_LIST.append(query)
            
common = Common()

def watch(site):
    global WATCH_FLAG
    for it in common.QUERY_WATCH:
        it = it.split('@')

        if((site['bjtime'].find(unicode(it[0],'utf-8')) != -1) and (site['siteName'].find(unicode(it[1],'utf-8')) != -1)):
            print '^O^'*3,site['bjtime'],
            WATCH_FLAG = True

def printSites(data):
    for site in data:
        # for key, value in site.items():
        #     print value,'\t',
        # print '\n'
        if(site['isClosed'] == 1):
            print 'closed',
        else:
            if(site['realSeats'] == 1):
                print '-> ^O^',
                watch(site)
            else:
                print '  full',
                
        print site['siteCode'],
        print site['siteName']
                
def printDates(data):
    for date in data:
        print date['bjTime']
        printSites(date['sites'])
        print ''

def printJson(data):
    print '-' * (WIDTH - 10)
    print '\t\t\trefreshed at', time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
    for city in data:
        # print city['city']
        printDates(city['dates'])
       
def query():
    global IS_LOGIN
    
    if(not IS_LOGIN):
        common.doLogin()

    info()

    for query in QUERY_LIST:
        echo = opener.open(query).read().decode('utf-8')
        data = json.loads(echo)
        if(type(data) is types.DictionaryType):
            IS_LOGIN = False
            return
        printJson(data)

def info():
    info = '\n' * HEIGHT
    info += '------------------------query GRE Seats------------------------------\n'
    info += 'Version     :%s (python/%s)\n' % (__version__, sys.version.partition(' ')[0])
    info += 'Query Site  :%s\n' % common.USERINFO_URL
    info += 'Query Month :%s\n' % unicode('|'.join(common.QUERY_MONTH), 'utf-8')
    info += 'Query City  :%s\n' % unicode('|'.join(common.QUERY_CITYCN), 'utf-8')
    info += 'Watch       :%s\n' % unicode('|'.join(common.QUERY_WATCH), 'utf-8')
    info += 'Contact     :%s' % 'yipeipei@gmail.com'
    print info

def main():
    # sys.setdefaultencoding('utf-8')
    common.genQuery()
    # echo = opener.open(QUERY_LIST[0]).read().decode('utf-8')
    # print echo
    while(True):
        query()
        # print WATCH_FLAG
        if(WATCH_FLAG):
            while(True):
                winsound.PlaySound(os.path.join(os.getcwd(), __ring__),winsound.SND_LOOP & winsound.SND_NOSTOP)
        else:
            time.sleep(common.QUERY_INTERVAL)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
