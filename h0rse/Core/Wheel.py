#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: Wheel.py
@time: 2019-5-5 10:59
@desc: HTTP请求、响应协议内容下的基本运行单元
@遗漏功能点：
    1. redirect设置，是否follow，跟踪几层
    2. Http Basic认证，https的兼容性
'''

from h0rse.Libs.Http import Url
from h0rse.Libs.Http import Request
from h0rse.Libs.Http import Response

import requests

#########################################################################
# 功能：扔进一个非标转化的url，在轮子负责将url标准化，填入请求头，发送后解析收到的响应包
# 调用：t = Wheel(url, 'get', headers)
#      reply = t.send()
# TODO: 加入一个Session功能存储cookie
# 一旦有某个response包含cookie，则添加进后续请求。
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
        self._cookie = None
        if self._cookie != None:
            self._headers.update(self._cookie)


    def send(self):
        if self._cookie != None:
            self._headers.update(self._cookie)
        request = Request.Request(self._url, self._method, headers= self._headers)
        ### TODO: delete it later, a warning handler
        if self._url.file_ext in ['ico', 'jpg', 'jpeg', 'gif', 'png', 'bmp', 'css', 'zip', 'rar', 'ttf']:
            print("这里我们没有处理干净，出错的url是{}，它的父url是{}".format(self._url.original_url,self._url.parent_url.original_url))
        ###
        req_meth = getattr(requests, self._method)
        if self._method == 'post':
            reply = req_meth(url=request.url, headers=request.headers, data=self._data, timeout=2)
        else:
            reply = req_meth(url=request.url, headers=request.headers, timeout=2)
        response = Response.toResponse(reply)
        if response.cookies is not None:
            self._cookie = response.cookies
        return response


'''
if __name__ =='__main__':
    target = '10.10.10.127:8080/WebGoat/login'
    t = Wheel(target, 'get', proxy='http://127.0.0.1:8080')
    r = t.send()
'''
#    print(r)

