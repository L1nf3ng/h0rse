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
from Configs.Config import  DEFAULT_ENCODING

# 对于re模块来说，输入必须是str对象，所以这里选择了response.text
#= re.search('charset=([^"]+")', response.text).group(1)

def toResponse(response):
    code = response.status_code
    msg = response.reason
    headers = response.headers
    charset = response.encoding
    raw_body = response.content
    return Response(code, msg, headers, charset, raw_body)

class Response:
    ##################################################################
    # @param: raw_body
    # @desc: raw_body这里传入的是bytes类，不能直接使用re下的匹配函数，
    #        因为re模块的匹配函数都是以str类输入，故需要处理一下
    ##################################################################
    def __init__(self,code, msg, headers, charset, raw_body):
        self._code = code
        self._msg = msg
        self._headers ={}
        self._headers.update(headers)
        # restore the rawbody in case you need to re-parse it in other form
        self._raw_body = raw_body
        self._charset,self._body = self.charset_handler(charset, raw_body)
        # extract cookies from header to use it easily
        self._cookies = self.cookies_handler(headers)

    def charset_handler(self,charset, raw_body):
        # when they are not same, search the headers and body to identify charset
        if charset != DEFAULT_ENCODING:
            # 1st, check the headers
            if "Content-Type" in self._headers.keys():
                # in the re pattern, check the alpha character and '-' symbol
                act_charset= re.search('charset=\s*?([\w-]+)',self._headers.get('Content-Type')).group(1)
                # 2nd, check the body
                if act_charset is None:
                    # first, transform rawbody to text class
                    text = raw_body.decode(self.charset)
                    act_charset = re.search('<meta.*?content=".*?charset=\s*?([\w-]+)"',text).group(1)
                    act_charset = act_charset.strip()
                # we've found charset in headers
                else:
                    act_charset = act_charset.strip()
        else:
            act_charset = charset
        # get the real body
        act_body = raw_body.decode(act_charset)
        return act_charset,act_body

    def cookies_handler(self,headers):
        if "Set-Cookie" in headers.keys():
            act_cookies = headers.get('Set-Cookie')
        else:
            act_cookies = None
        return act_cookies

    @property
    def code(self):
        return self._code

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
        outstr += "\r\n\r\n"
        outstr += self._body
        return outstr

if __name__=='__main__':
    import requests
    target ="https://butian.360.cn"
    resp =toResponse(requests.get(target))
    print(resp.cookies)
