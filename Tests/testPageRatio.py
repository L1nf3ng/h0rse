import unittest
import time
import requests
from Core.PageRatio import pageRaito, getVectors

class MyTestCase(unittest.TestCase):
    _url1 = 'https://xz.aliyun.com/t/5358'
    _url2 = 'https://xz.aliyun.com/t/5361'

    def testAliyun(self):
        past = time.time()
        txt1 = requests.get(self._url1).text
        txt2 = requests.get(self._url2).text
        period1 = time.time()
        v1 = getVectors(txt1)
        v2 = getVectors(txt2)
        period2 = time.time()
        print("Spend {}s to requsts".format((period1-past)))
        print("Spend {}s to compare".format((period2 - period1)))
        print(pageRaito(v1,v2))


if __name__ == '__main__':
    unittest.main()
