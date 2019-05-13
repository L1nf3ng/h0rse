# -*- encoding:utf-8 -*-

'''
    主要功能：
    捕获网站页面并解析获得所有的URL（暂时不包含分析、过滤）
    优化点：解析DOM树时采用事件驱动模型。
    功能遗漏点：细粒度的清洗控制，哪些类型的url不需要清洗
'''


from lxml.etree import parse, HTMLParser, fromstring
from urllib.parse import urlencode
from Core import Wheel
from Configs import Config
from Http.Url import Url
import time

STORE_FILE = '../tmp/index.html'

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
        if action is not None:
            self._urls.add(action)

    def _handle_form_tag_end(self,tag):
        pass


############################################################
# 使用Wheel类发送请求，收到并解析请求。
# 写入文件，方便调试，后期直接装入内存。
#
# %% 后期移除，或放到其他py中 %%
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
# 用xpath检索DOM树中的所有的form
# 并对这些form下的input子节点自动填值并构造post请求
# 其实这个方法并不适合web2.0
############################################################
def auto_fill(name):
    input_value_dict={
        'badb0y':['username','user','userid','nickname','name'],
        '123erty':['password','pass','pwd'],
        'tenaborn@bbb.com':['email','mail','usermail'],
        '13166771122':['mobile','telephone'],
        'h0rse is running for vulns.':['content','text','query','data','comment'],
        'www.test.com':['domain'],
        'http://h0rse.home.cn':['link','url','website']
    }
    p_val = 'h0rse'
    for key in input_value_dict.keys():
        # get the name_list from key
        if name in input_value_dict.get(key):
            p_val = key
    return p_val


def handle_form_with_xpath(tree):
#    ps = HTMLParser()
#    doc = parse(html, ps)
    forms = tree.xpath('//form')
    # there're no forms
    if forms == []:
        return []
    else:
        results = []
        for form in forms:
            temp = form.xpath('./@action')
            if temp==[]:
                # 没有action="abc/123/jdk.php"之类，则直接跳过
                continue
            base_url = temp[0]
            if base_url == '':
                continue
            inputs = form.xpath('./input')
            # here exists input labels
            params = {}
            if inputs != []:
                for input in inputs:
                    name = input.xpath('./@name')
                    if name == []:
                        continue
                    p_name = name[0]
                    value = input.xpath('./@value')
                    if value == []:
                        p_val = auto_fill(p_name)
                    else:
                        p_val = value[0]
                    params.update({p_name:p_val})
            if params != {}:
                # TODO：?拼接的方式，默认了form以get的方式请求数据，但实际上一个form表单有可能没有method，而它的提交完全由ajax来控制，后期需要解决一下（又是web2.0问题）。
                url = base_url+'?'+urlencode(params)
            else:
                url = base_url
            results.append(url)
    return results


############################################################
# 用xpath检索DOM树的函数
# 这里预留了一个全Url类组成的集合类Url_list
# 返回值： 标准化的Url class类，纠正了错误格式，但没有进行清洗
############################################################
'''
    这个函数目前需要承担多个解析任务，后期有可能拆分进不同的函数或类中。
    表单URL的提取（不仅仅包括action，还有其中带参数版）；
    不再使用set做去重工作，而是are_they_similar()函数
'''
def getURL_with_xpath(html, start_url):
    # frame 和 iframe 傻傻分不清
    Origin_Attrs = ['href', 'src', 'data', 'action']
    # @param Url_list,存储标准Url类的列表
    # @param url_list,存储粗提取的str类的url列表
    Url_list, url_list = [], []
    parser= HTMLParser()
    doc = fromstring(html,parser)
    # 1st Step, extract all urls by dom-tree.
    for rule in Origin_Attrs:
        temp = doc.xpath('//@%s'%rule)
        url_list.extend(temp)
    # 2nd Step, add some form urls:
    try:
        url_list.extend(handle_form_with_xpath(doc))
    except Exception as ext:
        print(ext,' --- current dom-tree don\'t contain forms or correct forms, the url is {}'.format(start_url.original_url))
    # 3rd Step, modify those urls which in wrong-format
    # to_modify stores the url to delete, then add the right-format urls
    to_modify = []
    for url in url_list:
        if not url.startswith('http://') and not url.startswith('https://'):
            to_modify.append(url)
    # add appropriate prefix
    for x in to_modify:
        url_list.remove(x)
        if not x.startswith('/'):
            x = '/'+x
        url_list.append(start_url.host+x)
    # 4th Step, translate the normal url to Url class
    for url in url_list:
        Url_list.append(Url(url))
    return Url_list


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
#   输入--未经清洗的Http.Url class集合
# TODO：加入对静态文件的过滤，特别是图片、媒体类，否则严重影响后面内容的解析
############################################################
def sanitize_urls(dirty_urls):
    # firstly, we define the file extension names to ignore
    # TODO:需要写一个针对js文件的URL提取代码，也即针对body的提取。
    ignore_file_ext=['ico', 'jpg','jpeg', 'gif', 'png', 'bmp', 'css', 'zip', 'rar', 'ttf']
    # secondly, we just sanitize the similar urls
    clean_urls = []
    for urld in dirty_urls:
        if urld.file_ext in ignore_file_ext:
            continue
        # 逻辑错误哟，应该检查完所有clean_url后再改变，否则可能重复添加
        AppendIt, ToDelete = True, None
        # clean_urls不为空则查重，为空直接添加
        if len(clean_urls)!=0:
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


############################################################
# 输出不符合标准格式的url类
#
# %% 后期移除，或放到测试代码中 %%
############################################################
def out_invalid(res):
    for x in res:
        if not x.startswith('http://') and not x.startswith('https://'):
            print(x)


if __name__ == '__main__':

    # retrieve_page(root_url)
    # now we start to parse the document

    past = time.time()
    url_set,domains = getURL_with_xpath(STORE_FILE)
    print('result len: ',len(url_set))
    now = time.time()
    print("we cost %ss time!"%(now-past))

#    print("here're some invalid urls:")
#    out_invalid(url_set)

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

