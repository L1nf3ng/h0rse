#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: Steering.py
@time: 2019-5-7 16:24
@desc:
    1. 发送速率的控制，协程数的设置
    2. 搜索策略的调整
    3. 未成功请求进入任务队列重新尝试
'''

from Core.Wheel import Wheel
from Core.Parser import getURL_with_xpath, sanitize_urls
from collections import deque

class Steering:
    def __init__(self):
        self._greenlet_num = 5
        self._send_freq = 10
        self._retry_times = 3
        # 探针深度，控制广度优先的搜索深度
        self._probe_depth = 3
        # 双向列表添加Url类
        self._task_queue = deque()

    def run(self,root_url):
        wheel = Wheel(root_url, 'get')
        Urls = getURL_with_xpath(wheel.send().body)
        self._task_queue.extend([u.canonical_url for u in sanitize_urls(Urls)])

    @property
    def task_queue(self):
        return self._task_queue

