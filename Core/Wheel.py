#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: Wheel.py
@time: 2019-5-5 10:59
@desc: A sender and receiver worked for http protocol.
'''

from Http import Url
from Http import Request
from Http import Response

import requests

#########################################################################
# 功能：扔进一个非标转化的url，在轮子负责将url标准化，填入请求头，发送后解析收到的响应包
# 调用：t = Wheel(url, 'get', headers)
#      reply = t.send()
#########################################################################

class Wheel:
    def __init__(self, url, method, headers=None, proxy=None, data=None):
        if not isinstance(url, Url.Url):
            self._url = Url.Url(url)
        else:
            self._url = url
        self._method = method.lower()
        # for now, only supports 6 methods from requests module
        if self._method not in ['get','post','put','delete','head','options']:
            raise ValueError("Not supported method!")
        self._data = None
        if self._method == 'post':
            self._data = data
        self._headers ={}
        if headers!= None:
            self._headers.update(headers)
        if proxy!= None:
            self._proxy ={'http':proxy ,'https':proxy}

    def send(self):
        request = Request.Request(self._url, self._method)
        req_meth = getattr(requests, self._method)
        if self._method == 'post':
            reply = req_meth(url=request.url, headers=request.headers, data=self._data)
        else:
            reply = req_meth(url=request.url, headers=request.headers)
        response = Response.toResponse(reply)
        return response


if __name__ =='__main__':
    target = '10.10.10.127:8080/WebGoat/login'
    t = Wheel(target, 'get', proxy='http://127.0.0.1:8080')
    r = t.send()
#    print(r)

