#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''
@author: d00ms(--)
@file: test_Parser.py
@time: 2019-5-7 14:56
@desc: Test Core.Parser Module
'''

from h0rse.Libs.Parser.Parser import are_they_similar,sanitize_urls, getForm_with_xpath
from h0rse.Libs.Http.Url import Url
import unittest


class TestIt(unittest.TestCase):
    def testSimilarity(self,urla,urlb):
        result = are_they_similar(urla,urlb)
        try:
            self.assertEqual(result, -1)
        except Exception as ext:
            print(ext)

    def testSanitization(self, dirty_urls):
        return sanitize_urls(dirty_urls)

    def testAutoFill(self,html):
        return getForm_with_xpath(html)


if __name__ == '__main__':
    t = TestIt()

    base = 'www.bat.com/index.php'
    t.testSimilarity(Url(base+'?b=4'), Url(base+'?b=3'))
    t.testSimilarity(Url(base+"?a=3"), Url(base+"?a=2&b=4"))
    t.testSimilarity(Url(base), Url(base))
    t.testSimilarity(Url(base), Url(base+"?a=2"))
    dirty_urls = [Url(base),Url(base+'?a=1'),Url(base+'?a=2'),Url(base+'?b=1'),Url(base+'?b=4&a=3'),Url(base+'?b=4&c=2')]
    clean_urls = t.testSanitization(dirty_urls)
#    for x in clean:
#        print(x.canonical_url)
    print("dirty urls:")
    print([x.canonical_url for x in dirty_urls])
    print([x.canonical_url for x in clean_urls])

    html1 = '''\
<form>
 First name:<br>
<input type="text" name="nickname">
<br>
 Last name:<br>
<input type="text" name="password">
</form>'''
    print(t.testAutoFill(html1))

    html2 = '''\
<form>
<input type="radio" name="sex" value="male" checked>Male
<br>
<input type="radio" name="sex" value="female">Female
</form> '''
    print(t.testAutoFill(html2))

