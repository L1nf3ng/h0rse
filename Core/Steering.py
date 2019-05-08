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
from Http.Url import Url

class Steering:
    def __init__(self):
        self._greenlet_num = 5
        self._send_freq = 10
        self._retry_times = 3
        # 探针深度，控制广度优先的搜索深度
        self._probe_depth = 3
        # 双向列表添加task，其中每个元素构成是(Url class, Search Depth)
        self._task_queue = deque()
        '''
        这里必须说明：谷仓类的目的——为了缓存每一层级的url对象，方便统计当前层级；
        层级控制的两种实现逻辑：
        实现逻辑1：当每个url爬取分析后获得的新url先做历史记录比较，然后加入谷仓，当队列空后，层级+1，并装入新的任务，清空谷仓，直到深度到达阈值。这种浪费了不少空间
        实现逻辑2：任务列表中除了记录url，还记录他的层级，实际上就是tuple。
        '''
        # self._task_granary = deque()
        self._history = deque()


    '''
        需要解决一下回路问题，也就是说在爬A网址时进入了B，在B中又进入了A，如此会造成大面积重复url
        方案：对爬行历史进行记录，建立hash表（set），再添加任务前检测是否出现过
        分歧：
        1. 将url的str填入历史set中，会出现两次url string => class的过程，但节省开支
        2. 将Url Class填入set中，但需要实现__eq__和__hash__，会产生额外内存开销
        3. 这里可以采用greenlet划分任务，当然，对任务队列和history的修改操作都要带锁
    '''
    def run(self,start_url):
        # 单线程模式
        # 为队列添加初始url
        self._task_queue.append((Url(start_url),0))
        # 先写一个完整的请求—响应—解析—更新的过称，然后循环
        while len(self._task_queue)!=0:
            base_url,current_depth = self._task_queue.popleft()
            if current_depth == self._probe_depth:
                break
            # send request
            self._history.append(base_url)
            wheel = Wheel(base_url, 'get')
            # get response
            reply = wheel.send()
            # 当前只处理正常返回200的页面，而不管301、302等重定向页面
            if reply.code != 200:
                continue
            Urls = getURL_with_xpath(reply.body, base_url)
            # filter out useful urls
            newUrls = sanitize_urls(Urls)
            # update the tasks and history
            for url in newUrls:
                if url not in self._history:
                    self._task_queue.append((url,current_depth+1))

    @property
    def history(self):
        return self._history

    @property
    def task_queue(self):
        return self._task_queue


if __name__ == '__main__':
    t = Steering()
    t.run('www.bandao.cn')
    print("we've searched {} urls".format(len(t.history)))
    print("there're {} urls left".format(len([x[0] for x in t.task_queue])))

