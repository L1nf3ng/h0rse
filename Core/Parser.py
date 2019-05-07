# -*- encoding:utf-8 -*-

'''
    主要功能：
    捕获网站页面并解析获得所有的URL（暂时不包含分析、过滤）
    优化点：解析DOM树时采用事件驱动模型。
    功能遗漏点：细粒度的清洗控制，哪些类型的url不需要清洗
'''


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
# 使用Wheel类发送请求，收到并解析请求。
# 写入文件，方便调试，后期直接装入内存。
#
# %% 后期移除，或送到其他py中 %%
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


############################################################
# 描述：
#   1. 功能：去含、去似，因为对于渗透测试，这类url只需要测试一项就行了
#   2. 参数：Http.Url.Url class
#   3. 返回值，代表两者的不同状态：
#       -1 <=> 完全不同;0 <=> 两者相同;1 <=> 左边大;2<=> 右边大
############################################################
def are_they_similar(urla, urlb):
    if urla.scheme != urlb.scheme:
        return -1
    elif urla.host != urlb.host:
        return -1
    elif urla.port != urlb.port:
        return -1
    elif urla.path != urlb.path:
        return -1
    if urla.params != dict() or urlb.params != dict():
        # analyse their parameters relationship
        # transform their parameter name into two categories
        s1 = set(urla.params.keys())
        s2 = set(urlb.params.keys())
        temp = s1 & s2
        # 两个集合取交集来判断包含关系:
        if temp == set():    # 空集合代表绝不包含
            return -1
        elif len(s1) == len(temp) and len(s1) == len(s2): # 完全同类
            return 0
        elif len(temp) < len(s1) and len(temp) < len(s2): # 部分参数重合，但还是不同的url
            return -1
        elif len(temp) == len(s2): # 包含关系，左边包含右边
            return 1
        else:   # 包含关系，右边包含左边
            return 2
    else:
        return 0


############################################################
# 提取有价值的url
# 功能：
#   1. 多类url的去似去含
#   2. 表单的自动填充，生成url，也即post类url
# 参数：
#   输入--未经清洗的Http.Url.Url集合
############################################################
def sanitize_urls(dirty_urls):
    # the first implements: we just sanitize the similar urls
    clean_urls = [dirty_urls[0]]
    for urld in dirty_urls:
        # 逻辑错误哟，应该检查完所有clean_url后再改变，否则可能重复添加
        AppendIt, ToDelete = True, None
        for urlc in clean_urls:
            temp = are_they_similar(urld,urlc)
            # 有相同url或包含某条url，则添加（删除）；否则添加之
            if temp == 0:
                AppendIt = False
            if temp == 1:
                # append the left one, ie. dirty_url
                ToDelete = urlc
        if AppendIt:
            clean_urls.append(urld)
        if ToDelete!= None:
            clean_urls.remove(ToDelete)
    return clean_urls


def out_invalid(res):
    for x in res:
        if not x.startswith('http://') and not x.startswith('https://'):
            print(x)


if __name__ == '__main__':

    # retrieve_page(root_url)
    # now we start to parse the document

    past = time.time()
    res2,domains = parse_with_xpath(STORE_FILE)
    print('result len: ',len(res2))
    now = time.time()
    print("we cost %ss time!"%(now-past))

#    print("here're some invalid urls:")
#    out_invalid(res2)

    print('We get these sub domains: it\'s totally {} domains'.format(len(domains)))
    for domain in domains:
        print(domain)

    '''
    past = time.time()
    t= MyParser()
    parser = HTMLParser(target=t)
    res1 = parse(store_file,parser)
    print('result len: ',len(res1))
    now = time.time()
    print("we cost %ss time!"%(now-past))
    '''
