#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: PageRatio.py
@time: 2019-5-7 16:21
@desc: 页面相似度算法
@reference: 百度2009年的专利
@procedures:
    1)将DOM树划分成不同的特征单元（节点、兄弟节点、子节点等形成的组合）
    2)特征单元映射出高维特征向量的维数（<标签名+属性值> ==hash==> 数值，推荐属性：id、class、name、style）
    3)对特征向量根据规则分配权值（同一特征向量在DOM里多次出现就将权值累加，这一步其实可以在最后一步压缩时完成）：
        <1>随节点深度的增加而递减，可采用等比递减；
        <2>权值随重复兄弟节点的增加而递减
        <3>权值随特征单元无相关属性而递减
    4)将所得权值作为特征向量对应维数的数值，最后将结果映射成N维的向量，存储比较。
P.S.
    https://www.4hou.com/penetration/18447.html
    https://www.4hou.com/web/17568.html
    https://www.freebuf.com/vuls/203907.html
TODO: 在进行相似度查找时，需要检索大量的数据，专利中采用了一种基于网格的算法，可以一看。
'''

import math
import hashlib
import difflib
from lxml import etree
from collections import deque

# use modifier later
def extend(seq, node, depth):
    for child in node.getchildren():
        # 坑点1 -->isinstance和type的区别
        if type(child)== etree._Element:
            seq.append((child, depth+1))

# custom a special zip func
def myZip( seq1, seq2):
    newDict = {}
    for key in range(0,len(seq1)):
        newDict.update( {seq1[key]:seq2[key]} )
    return newDict

# the two parameters must occur one
def getPropertyVectors(strings=None, filepath=None):

    # 衰减因子，数值越大代表衰减越厉害
    decay1, decay2 = 0.4, 0.6
    # 先试试压缩到1000维特征向量的效果，取余操作，故第1000号元素无值
    vectors = [0.0]*1000
    ## 1.选取每个节点作为特征向量
    ATTRIBS = ['id','name','class','style']

    # the first node which contains no attributes
    if strings == None:
        path = filepath
        doc = etree.parse(path, etree.HTMLParser())
        root = doc.getroot()
    else:
        root = etree.fromstring(strings, etree.HTMLParser())

    # the nodeSeq contains nodes which will be parsed later
    nodeSeq = deque()
    extend(nodeSeq, root, 0)
    # define two lists, the first is dimensions, the second is weights
    dimens, weights = [],[]
    # the zip two lists above into a dictionary finally
    # P.S. array to debug
    names = []
    while len(nodeSeq)!=0:
        node,depth = nodeSeq.popleft()
        extend(nodeSeq, node, depth)
        # a variable to help define the property factor
        sector = 0.0
        charCode = "<"+ node.tag
        for attr in node.keys():
            if attr in ATTRIBS:
                charCode += " " + attr + "=" + node.get(attr)
                sector += 0.25
        charCode += ">"
    ## 2.用哈希算法md5完成映射
        tom = hashlib.md5()
        tom.update(charCode.encode('utf8'))
        dimension = int(tom.hexdigest(), 16)
        dimens.append(dimension)
    ## 3.按规则计算其权重值，初始权值都是1.0，乘以各种衰减因子递退
        # 1st factor, the depth of tree
        depthFactor = decay1**depth
        # 2nd factor, the duplication distance
        dupFactor = 1.0
        for iter in range(0, len(dimens)-1):
            # no need to check the last one, cause it's newest dimension
            # 这里比较重复率时，我们只考虑最早出现的重复节点的距离
            if dimens[iter] == dimension:
                dupFactor *= decay2**(len(dimens)-1-iter)
                break
        # 3rd factor, the properties numbers
        propFactor = 1.0 * sector
        # so, in this formula, the most important = 1.6
        weights.append(0.8*depthFactor + 0.5*dupFactor + 0.3*propFactor)
        names.append(node.tag)
    '''
    # 一些中间结果的测试代码
    matrix = list(zip(dimens, weights))
    results = list(zip(names, matrix))
    # 不要转换成字典，因为在生成字典时会发生key碰撞
    for item in results:
        print(item)
    '''
    ## 4.压缩产生N维特征向量（例如：N=1000）
    for iter in range(0,len(dimens)):
        vectors[dimens[iter]%1000] += weights[iter]
    '''
    for iter in range(0,len(vectors)):
        print("维数：{} 权值：{}".format(iter, vectors[iter]))
    '''
    return vectors

# get difference ratio from two proper vectors
def pageStructureRaito(vec1, vec2):
    '''
    欧式距离和余弦相似度的区别：
        余弦相似度衡量的是维度间取值方向的一致性，注重维度之间的差异，不注重数值上的差异，而欧氏度量的正是数值上的差异性。
    :param vec1: proper vectors of webpage1
    :param vec2: proper vectors of webpage2
    :return: diff ratio in cosine distance
    '''
    numerator, deno1, deno2 = 0.0, 0.0, 0.0
    for iter in range(0,len(vec1)):
        numerator += vec1[iter]*vec2[iter]
    for iter in range(0,len(vec1)):
        deno1 += vec1[iter]*vec1[iter]
        deno2 += vec2[iter]*vec2[iter]

    return numerator/(math.sqrt(deno1*deno2))

def pageContentRatio(body1, body2):
    matcher = difflib.SequenceMatcher()
    matcher.set_seqs(body1, body2)
    return matcher.ratio()
