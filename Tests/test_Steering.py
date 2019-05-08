#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: test_Steering.py
@time: 2019-5-8 13:26
@desc: Test the functions from Steering
'''

import unittest
from collections import deque
from Core.Steering import Steering
from Http.Url import Url

class Tester (unittest.TestCase):
    def testGo(self):
        s = Steering()
        root_url = 'www.bandao.cn'
        s.run(root_url)
        print(s.task_queue)


if __name__ == '__main__':
#  t =Tester()
#  t.testGo()
    base = 'www.baidu.com/index.php'
    e1,e2  = Url(base),Url(base)
    s2= deque([e1,Url(base+'?a=1'),Url(base+'?a=2'),Url(base+'?b=1'),Url(base+'?b=4&a=3'),Url(base+'?b=4&c=2')])
    s1 = {'a','b','c','d','e'}

    print(e2 in s2)
