import unittest
import requests

from Http.Response import Response, toResponse


class MyTestCase(unittest.TestCase):
    def test_special(self):
        resp = requests.get('http://news.bandao.cn/lagala/')
        return toResponse(resp)

if __name__ == '__main__':
    unittest.main()
