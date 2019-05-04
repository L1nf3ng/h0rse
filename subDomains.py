# -*- encoding:utf-8 -*-
# 主要功能：
# 捕获网站页面并解析获得所有的URL（暂时不包含分析、过滤）
# 优化点：解析DOM树时采用事件驱动模型，

from lxml.etree import parse, HTMLParser
import requests
import time


root_url = 'http://www.bandao.cn'
store_file = 'tmp/index.html'

# frame 和 iframe 傻傻分不清
Origin_Tags = ['a','img','link','script','iframe','frame','form','object']
Origin_Attrs = ['href', 'src', 'data', 'action']

def retrieve_page(url):
    # 打开文件时必须设置一下encoding，否则在win平台下默认以gbk来解析
    with open(store_file,'w',encoding= 'utf8') as file:
        rep = requests.get(url)
        # 许多网页默认返回的encoding是iso-8859-1，这是一种单字节的编码形式，实际编码还得依据charset说明。
        text = rep.content.decode('utf-8')
        file.write(text)

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


def parse_with_officialParser(file):
    global Origin_Attrs
    res2= set()
    parser= HTMLParser()
    doc = parse(file,parser)
    for rule in Origin_Attrs:
        temp = doc.xpath('//@%s'%rule)
        res2.update(temp)
    return res2

if __name__ == '__main__':
    # now we start to parse the document
    past = time.time()
    t= MyParser()
    parser = HTMLParser(target=t)
    res1 = parse(store_file,parser)
    print('result len: ',len(res1))
    now = time.time()
    print("we cost %ss time!"%(now-past))

    past = time.time()
    res2 = parse_with_officialParser(store_file)
    print('result len: ',len(res2))
    now = time.time()
    print("we cost %ss time!"%(now-past))

    def out_invalid(res):
        for x in res:
            if not x.startswith('http://') and not x.startswith('https://'):
                print(x)
