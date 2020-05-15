#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

# This is dooms aka toothKing from somewhere unknown, who has exercised for two years and a half on programming.
# Focus on his program and you can support him by donating him ¥1. Save the child please.
# @Time    : 2020-5-15 10:48
# @Author  : dooms
# @File    : Schedule.py
# @Desc    : 主要的调度逻辑，抽象地说就是生产者 --> 消费者模型

class Schedular:

    def __init__(self):
        self._task_list = []

    '''
        初始化模块，创建任务
    '''
    def craete_tasks(self, module):
        # ...
        # ...
        self._task_list.append(module)

    '''
        参照事件循环模型，开始执行
    '''
    def run(self):
        # ...
        # ...
        # allJobs.run()
        pass

