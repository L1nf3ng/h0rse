'''
这个包进行与HTTP有关的三大元素的封装
1.URL类，主要补全缺省url
2.Request类，记录header、cookie等重要信息，同时也是可以用的注入点
3.Response类，记录相应信息，其中Server、X-Proxy-Cache等信息很重要，也方便后期输出到Web、日志能进行分析
'''