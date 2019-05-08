#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: test_Steering.py
@time: 2019-5-8 13:26
@desc: Test the functions from Steering
'''

import unittest
from Core.Steering import Steering


class Tester (unittest.TestCase):
    def testGo(self):
        s = Steering()
        root_url = 'www.bandao.cn'
        s.run(root_url)
        print(s.task_queue)


if __name__ == '__main__':
  t =Tester()
  t.testGo()
