#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: Response.py
@time: 2019-4-30 11:15
@desc: 记录有用的重要信息，如Server、X-Proxy-Cache等
       另外，写一个第三方库的Response对象向本相应类的转换函数，例如requests库
'''

# for Requests.Response

import re
from ..Config.Config import  DEFAULT_ENCODING

def toResponse(response):
    code = response.status_code
    msg = response.reason
    req_url = response.url
    headers = response.headers
    charset = response.encoding
    raw_body = response.content
    return Response(code, msg, req_url, headers, charset, raw_body)

class Response:
    ##################################################################
    # @param: raw_body
    # @desc: raw_body这里传入的是bytes类，不能直接使用re下的匹配函数，
    #        因为re模块的匹配函数都是以str类输入，故需要处理一下
    ##################################################################
    def __init__(self,code, msg, url, headers, charset, raw_body):
        self._code = code
        self._msg = msg
        self._req_url = url
        self._headers ={}
        self._headers.update(headers)
        # restore the rawbody in case you need to re-parse it in other form
        self._raw_body = raw_body

        try:
            self._charset,self._body = self.charset_handler(charset, raw_body)
        except Exception:
            print('Exception comes from: {}'.format(self._req_url))

        # deal with the AttributeError in outer loop
#        self._charset, self._body = self.charset_handler(charset, raw_body)
        # extract cookies from header to use it easily
        self._cookies = self.cookies_handler(headers)

    def charset_handler(self,charset, raw_body):
        #TODO： 首先判断是否有报文，然后再判定其编码形式，实际上这部分可以用chardet模块替代
        # when they are not same, search the headers and body to identify charset
        if self._headers.get("Content-Length")=='0' and raw_body==b'':
            return DEFAULT_ENCODING, ''
        if charset != DEFAULT_ENCODING:
            # 1st, check the headers
            if "Content-Type" in self._headers.keys():
                # in the re pattern, check the alpha character and '-' symbol
                charset_mo = re.search('charset=\s*?([\w-]+)',self._headers.get('Content-Type'))
                # we've found charset in headers
                if charset_mo != None:
                    act_charset = charset_mo.group(1).strip()

                # 2nd, check the body
                else:
                    if charset != None:
                        # first, transform rawbody to text class
                        text = raw_body.decode(charset)
                        charset_mo = re.search('<meta.*?content=".*?charset=\s*?([\w-]+)"',text)
                        # we've found charset in body
                        if charset_mo != None:
                            act_charset = charset_mo.group(1).strip()
                        else:
                            act_charset = DEFAULT_ENCODING
                    else:
                        act_charset=DEFAULT_ENCODING
        else:
            act_charset = DEFAULT_ENCODING
        # get the real body
        try:
            act_body = raw_body.decode(act_charset)
        except:
            act_charset= 'gbk'
            act_body = raw_body.decode(act_charset)
        return act_charset,act_body

    def cookies_handler(self,headers):
        if "Set-Cookie" in headers.keys():
            act_cookies = {'Cookie':headers.get('Set-Cookie')}
        else:
            act_cookies = None
        return act_cookies

    @property
    def code(self):
        return self._code

    @property
    def req_url(self):
        return self._req_url

    @property
    def headers(self):
        return self._headers

    @property
    def body(self):
        return self._body

    @property
    def charset(self):
        return self._charset

    @charset.setter
    def charset(self,charset):
        self._charset = charset
        self._body = self._raw_body.decode(charset)

    @property
    def cookies(self):
        return self._cookies

    def __str__(self):
        outstr = ""
        outstr += "HTTP/1.1 {} {}\r\n".format(self._code, self._msg)
        for key in self._headers.keys():
            outstr += "{}: {}\r\n".format(key,self._headers.get(key))
        outstr += "\r\n"
        outstr += self._body
        return outstr

if __name__=='__main__':
    import requests
    target ="https://butian.360.cn"
    resp =toResponse(requests.get(target))
    print(resp.cookies)
