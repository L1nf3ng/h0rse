import unittest
import time
import requests
from Core.PageRatio import pageRaito, getVectors

class MyTestCase(unittest.TestCase):
    _url1 = 'https://www.freebuf.com/sectool/205207.html'
    _url2 = 'https://www.freebuf.com/vuls/205206.html'
    _url3 = 'https://www.freebuf.com'

    def testAliyun(self):
        past = time.time()
        txt1 = requests.get(self._url1).text
        txt2 = requests.get(self._url2).text
        txt3 = requests.get(self._url3).text
        period1 = time.time()
        v1 = getVectors(txt1)
        v2 = getVectors(txt2)
        v3 = getVectors(txt3)
        period2 = time.time()
#        print("Spend {}s to requsts".format((period1-past)))
#        print("Spend {}s to compare".format((period2 - period1)))
        print(pageRaito(v1,v2))
        print(pageRaito(v1,v3))

if __name__ == '__main__':
    unittest.main()
