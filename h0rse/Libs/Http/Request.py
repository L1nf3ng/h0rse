#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: Request.py
@time: 2019-4-30 11:15
@desc: 记录header、cookie等重要信息
'''

from ..Config import Config
from . import Url

class Request:

    # 除了前面几个必须的参数，后面的参数用来定制化
    def __init__(self,url,method='GET', headers=None, user_agent=Config.DEFAULT_USER_AGENT,
                 referer=None, cookies=None, data=None):      # data parameter only used in post method！
        if isinstance(url,Url):
            self._url = url
        else:
            self._url = Url(url)
        self._method = method.upper()

        self._headers = {}
        if isinstance(headers, dict):
            self._headers.update(headers)
        else:
            pass
        self._referer = referer
        self._user_agent = user_agent
        self._cookies = cookies
        # here we update the _headers attr:
        self._headers.update({"Referer":self._referer})
        self._headers.update({"User-Agent":self._user_agent})
        self._headers.update({"Cookies":self._cookies})
        self._post_data = data

    # some common setter/getter for properties, some setters associated with headers must update in time!
    @property
    def url(self):
        return self._url.canonical_url


    @url.setter
    def url(self, url):
        if isinstance(url,Url):
            self._url = url
        else:
            self._url = Url(url)

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self,headers):
        if isinstance(headers, dict):
            self._headers.update(headers)
        else:
            raise ValueError

    @property
    def referer(self):
        return self._referer

    @referer.setter
    def referer(self,referer):
        self._referer= referer
        self._headers.update({"Referer":referer})

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self,user_agent):
        self._user_agent= user_agent
        self._headers.update({"User-Agent":user_agent})

    @property
    def post_data(self):
        return self._post_data

    @post_data.setter
    def post_data(self,data):
        self._post_data = data

    def __str__(self):
        outstr =  ""
        outstr +="{} {} HTTP/1.1\r\n".format(self._method, self._url.path)
        outstr +="Host:{}\r\n".format(self._url.host)
        for key in self._headers.keys():
                outstr += "{}: {}\r\n".format(key, self._headers.get(key))
        outstr += "\r\n"
        if self._method=="POST" :
            outstr+="{}\r\n".format(self._post_data)
        return outstr

if __name__=='__main__':
    urlstring = 'www.google.com/tools/f4ck/index.phtml?a=2134&rb=414#fdfo'
    print(Request(urlstring,'post',data='a=123&b=456'))

