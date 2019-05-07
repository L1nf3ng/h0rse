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
    def testSimilarity(self,urla,urlb):
        result = are_they_similar(urla,urlb)
        try:
            self.assertEqual(result, -1)
        except Exception as ext:
            print(ext)


if __name__ == '__main__' :
    base = 'www.bat.com/index.php'
    t = TestIt()
    t.testSimilarity(Url(base+'?b=4'), Url(base+'?b=3'))
    t.testSimilarity(Url(base+"?a=3"), Url(base+"?a=2&b=4"))
