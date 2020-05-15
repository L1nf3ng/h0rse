import unittest

# import time
import requests
from h0rse.Libs.Misc.PageRatio import pageStructureRaito, getPropertyVectors, pageContentRatio

class MyTestCase(unittest.TestCase):
    _url1 = 'http://china.huisou.com/so/sale/k-rtyy.html'
    _url2 = 'http://china.huisou.com/so/sale/k-4324.html'
    _url3 = 'http://10.10.10.127:3000/#/search?q=orange\''

    def testAliyun(self):
#        past = time.time()
        txt1 = requests.get(self._url1).text
        txt2 = requests.get(self._url2).text
#        txt3 = requests.get(self._url3).text
#        period1 = time.time()
        print(pageContentRatio(txt1, txt2))

        v1 = getPropertyVectors(txt1)
        v2 = getPropertyVectors(txt2)
#        v3 = getPropertyVectors(txt3)
#        period2 = time.time()
        print(pageStructureRaito(v1, v2))
#        print(pageStructureRaito(v2,v3))
#        print("Spend {}s to requsts".format((period1-past)))
#        print("Spend {}s to compare".format((period2 - period1)))


if __name__ == '__main__':
    unittest.main()
