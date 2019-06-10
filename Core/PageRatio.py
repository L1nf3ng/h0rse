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
    2)特征单元映射出高维特征向量（<标签名+属性值> ==hash==> 数值，推荐属性：id、class、name、style）
    3)对特征向量根据规则分配权值：
        <1>随节点深度的增加而递减，可采用等比递减；
        <2>权值随重复兄弟节点的增加而递减
        <3>权值随特征单元无相关属性而递减
@addons:
    在进行相似度查找时，需要检索大量的数据，专利中采用了一种基于网格的算法。后面可以一看。
P.S.
    今天好累，回去睡了啦
    https://www.4hou.com/penetration/18447.html
    https://www.4hou.com/web/17568.html
    https://www.freebuf.com/vuls/203907.html
'''


