from django.test import TestCase
from .services import notification
# Create your tests here.

class KeeperTest (TestCase):


    def testSendEmail(self):
        try:
            notification.send_email('Hello, Title', 'This is a test mail', 'avrilmaomao@qq.com')
        except BaseException as e:
            self.assertTrue(False, 'Send mail exception')