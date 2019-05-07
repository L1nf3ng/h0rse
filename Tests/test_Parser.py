#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: test_Parser.py
@time: 2019-5-7 14:56
@desc: Test Core.Parser Module
'''

from Core.Parser import are_they_similar
from Http.Url import Url
import unittest


class TestIt(unittest.TestCase):
    def testRun(self,urla,urlb):
        try:
            self.assertTrue(are_they_similar(urla,urlb),
                        "{} {} they're not similar".format(urla.original_url,urlb.original_url))
        except Exception as ext:
            print(ext)

if __name__ == '__main__' :
    base = 'www.bat.com/index.php'
    t = TestIt()
    t.testRun(Url(base+'?a=1'), Url(base+'?b=3'))
    t.testRun(Url(base+"?a=3"), Url(base+"?a=2&b=4"))
