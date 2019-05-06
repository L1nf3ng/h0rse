# -*- encoding:utf-8 -*-
# 主要功能：
# 捕获网站页面并解析获得所有的URL（暂时不包含分析、过滤）
# 优化点：解析DOM树时采用事件驱动模型，

from lxml.etree import parse, HTMLParser
from Core import Wheel
from Configs import Config
from Http.Url import Url
import time


ROOT_URL = 'www.bandao.cn'
STORE_FILE = '../tmp/index.html'

# frame 和 iframe 傻傻分不清
Origin_Tags = ['a','img','link','script','iframe','frame','form','object']
Origin_Attrs = ['href', 'src', 'data', 'action']

############################################################
# 使用Wheel类发送请求，收到并解析请求。
# 写入文件，方便调试，后期直接装入内存。
############################################################
def retrieve_page(url):
    # 打开文件时必须设置一下encoding，否则在win平台下默认以gbk来解析
    global STORE_FILE
    with open(STORE_FILE,'w',encoding= Config.DEFAULT_ENCODING) as file:
        # 许多网页默认返回的encoding是iso-8859-1，这是一种单字节的编码形式，实际编码还得依据charset说明。
        t = Wheel.Wheel(url, 'get')
        r = t.send()
        file.write(r.body)


############################################################
#
# HTMLParser的自实现类，实现了start、end、close三个事件的回调函数
# 对特定标签做了特殊处理，目前测试效果不如建立整棵树后用xpath检索的效果
#
############################################################
class MyParser:
    def __init__(self):
        self._urls = set()

    # 事件 1
    def start(self,tag,attrs):
        # python的getattr方法类似于Java的反射机制
        # 方法原型：getattr(object, method_name, default_method)
        # attrs举例：{'src':'http://13232','method':'put'} == item() ==> [(,)...]
        global Origin_Attrs, Origin_Tags
        meth = getattr(self, '_handle_'+tag+'_tag_start', lambda *args:None)
        # step1, 运行定制化处理函数
        meth(tag, attrs)
        # step2, 检查每个标签并提取标签
        if tag in Origin_Tags:
            for item in attrs.items():
                if item[0] in Origin_Attrs:
                    self._urls.add(item[1])

    # 事件 2
    def end(self, tag):
        meth = getattr(self, '_handle_' + tag + '_tag_end', lambda arg: None)
        meth(tag)

    # 事件 3 -- 所有标签处理结束后执行
    def close(self):
        return self._urls

    # 预留一个处理头信息url的函数
    def _handle_headers_urls(self):
        pass

    # 预留一个处理文本url的函数
    def _handle_text_urls(self):
        pass

    # 定制化处理表单内url
    def _handle_form_tag_start(self,tag,attrs):
        action = attrs.get('action', None)
#        print("WE get into a form tag, and the url is ",action)
        if action is not None:
            self._urls.add(action)
#            print("Successful adding")

    def _handle_form_tag_end(self,tag):
        pass
#        print("Went out a form tag. Just now, we didn't make a request.")


############################################################
# 用xpath检索DOM树的函数
# 这里预留了一个全Url类组成的集合类Url_set，后期要用时可以return一下
############################################################
def parse_with_xpath(file):
    global Origin_Attrs
    global ROOT_URL
    Url_set, res2,domains = set(),set(),set()
    parser= HTMLParser()
    doc = parse(file,parser)
    for rule in Origin_Attrs:
        temp = doc.xpath('//@%s'%rule)
        res2.update(temp)
    # get the incorrect urls
    to_remove = []
    for url in res2:
        if not url.startswith('http://') and not url.startswith('https://'):
            to_remove.append(url)
    # add appropriate prefix
    for x in to_remove:
        res2.remove(x)
        if not x.startswith('/'):
            x = '/'+x
        res2.add(ROOT_URL+x)
    # translate the normal url to Url class
    for url in res2:
        Url_set.add(Url(url))
    for url in Url_set:
        domains.add(url.host)
    return res2, domains


def out_invalid(res):
    for x in res:
        if not x.startswith('http://') and not x.startswith('https://'):
            print(x)


if __name__ == '__main__':

    # retrieve_page(root_url)
    # now we start to parse the document

    '''
    past = time.time()
    t= MyParser()
    parser = HTMLParser(target=t)
    res1 = parse(store_file,parser)
    print('result len: ',len(res1))
    now = time.time()
    print("we cost %ss time!"%(now-past))
    '''

    past = time.time()
    res2,domains = parse_with_xpath(STORE_FILE)
    print('result len: ',len(res2))
    now = time.time()
    print("we cost %ss time!"%(now-past))

#    print("here're some invalid urls:")
#    out_invalid(res2)

#    print('We get these sub domains:')
#    for domain in domains:
#        print(domain)
