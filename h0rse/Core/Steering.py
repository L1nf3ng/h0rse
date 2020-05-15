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


from Wheel import Wheel
from Parser import getURL_with_xpath, sanitize_urls
from collections import deque
from h0rse.Libs.Http.Url import Url

import sys

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
        self._failure_req = deque()

    '''
        需要解决一下回路问题，也就是说在爬A网址时进入了B，在B中又进入了A，如此会造成大面积重复url
        方案：对爬行历史进行记录，建立hash表（set），再添加任务前检测是否出现过
        分歧：
        1. 将url的str填入历史set中，会出现两次url string => class的过程，但节省开支
        2. 将Url Class填入set中，但需要实现__eq__和__hash__，会产生额外内存开销
        3. 这里可以采用greenlet划分任务，当然，对任务队列和history的修改操作都要带锁
    '''
    def run(self,start_url, headers= None):
        # 单线程模式
        # 为队列添加初始url
        ignore_file_ext = ['ico', 'jpg', 'jpeg', 'gif', 'png', 'bmp', 'css', 'zip', 'rar', 'ttf']
        special_ext = ['doc','docx','xls','xlsx','csv']
        if not isinstance(start_url,Url):
            start_url = Url(start_url)
            start_url.parent_url = 'https://www.baidu.com'
        self._task_queue.append((start_url,0))
        # 先写一个完整的请求—响应—解析—更新的过称，然后循环
        while len(self._task_queue)!=0:
            base_url,current_depth = self._task_queue.popleft()
            if current_depth == self._probe_depth:
                break
            # 特殊后缀，如可下载文件则跳过检测，但输出url地址
            if base_url.file_ext in special_ext:
                print('Downloadable Files: {}'.format(base_url.canonical_url))
                continue
            # 两次过滤，一次在任务队列弹出时，另一次在添加入任务队列时。
            if base_url.file_ext in ignore_file_ext:
                continue
            # send request
            self._history.append(base_url)
            wheel = Wheel(base_url, 'get' ,headers= headers)
            # get response
            '''
            except AttributeError as ext:
                print("Response parsing error. Please check the url:{}".format(base_url.original_url))
                traceback.print_exc()
                continue
            '''
            try:
                reply = wheel.send()
            except Exception:
                # if requests fail, we should ignore the following parsing process.
                print('Connection errors happened in: {}'.format(base_url.original_url))
                self._failure_req.append(base_url)
                continue
            # 当前只处理正常返回200的页面，而不管301、302等重定向页面
            if reply.code != 200 or reply.body=='':
                continue
            # get the dirty Urls, so it's time to add the father url here
            try:
                Urls = getURL_with_xpath(reply.body, base_url)
            except AttributeError as ext:
                print(ext,' and the source is: {}'.format(reply.req_url))
                continue
            # filter out useful urls
            newUrls = sanitize_urls(Urls)

            # update the tasks and history
            for url in newUrls:
                if url not in self._history:
                    self._task_queue.append((url,current_depth+1))

            print("we've searched {} urls, current depth is {}".format(len(self._history), current_depth))
            print("there're {} urls left".format(len([x[0] for x in self._task_queue])))


    @property
    def history(self):
        return self._history

    @property
    def task_queue(self):
        return self._task_queue


if __name__ == '__main__':
#    header = {'Cookie': 'security=low; security_level=0; PHPSESSID=48lfcvid2ede63nka9vgea52a3;
#      acopendivids=swingset,jotto,phpbb2,redmine; acgroupswithpersist=nada'}

    print(sys.path)
    t = Steering()
    t.run('http://10.10.10.108/dvwa')
    print("we've searched {} urls".format(len(t.history)))
    print("there're {} urls left".format(len([x[0] for x in t.task_queue])))

