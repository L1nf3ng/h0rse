#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: Url.py
@time: 2019-4-30 11:15
@desc: 封装URL类，主要补全缺省url
'''


from Configs import Config

from urllib.parse import  urlparse

class Url:
    def __init__(self, urlString,encoding=Config.DEFAULT_ENCODING):
        # 先补齐协议名、端口名
        if not urlString.startswith('http://') and not urlString.startswith('https://'):
            urlString = 'http://'+urlString
        result = urlparse(urlString)
        self._host = result.hostname
        self._path = result.path
        if result.port is None:
            self._port= 80 if result.scheme=='http' else 443
        self._params = result.params
        self._filename = result.path[result.path.rfind('/')+1:]
        self._file_ext = None if self._filename == None else result.path[result.path.index('.')+1:]
        self._fragment = result.fragment

    @property
    def fragment(self):
        return self._fragment

    @property
    def host(self):
        return self._host

    @property
    def path(self):
        return self._path

    # generate a standard url to feed the request method: get、post、put、head
    # TODO: finish it tomorrow!
    @property
    def canonical_url(self):
        pass

    def __str__(self):
        return "the 6-elements tuple is: %s %s %s %s %s %s"%(self._host, str(self._port), self._path, self._filename, self._file_ext, self._params)


if __name__=='__main__':
    # some tests for url class
    t_url = 'http://www.goodle.com/index.pphjp?a=2134&rb=414#fdfo'
    xt= Url(t_url)
    print(xt, ' additional: ',xt.fragment)
    print("original url string: ",xt.canonical_url)
