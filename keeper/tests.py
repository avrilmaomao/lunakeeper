import typing

from django.test import TestCase,Client
from django.urls import reverse
from django.utils.timezone import now
from django.core import mail

from .services import notification
from .models import Pony,History
from .consts import NOTIFY_CHANNEL_EMAIL,NOTIFY_CHANNEL_SLACK
from .views import check_and_get_pony
from .utils import hash_password

# Create your tests here.

EXISTED_PONY_NAME = 'dali01'
EXISTED_PONY_PASSCODE = 'pass001'


def add_testing_pony():
    if get_testing_pony() is not None:
        print("Testing pony already added")
        return
    pony = Pony(
        name=EXISTED_PONY_NAME,
        passcode=hash_password(EXISTED_PONY_PASSCODE),
        dark_minute=5,
        notify_channel=NOTIFY_CHANNEL_EMAIL,
        notify_url='luna@equestria.org',
        create_time=now()
    )
    pony.save()
    print("Testing Pony added")


def get_testing_pony() -> typing.Optional[Pony]:
    try:
        return Pony.objects.get(name=EXISTED_PONY_NAME)
    except Pony.DoesNotExist:
        return None
    except BaseException:
        raise

class KeeperTest (TestCase):

    @classmethod
    def setUpTestData(cls):
        add_testing_pony()

    def setUp(self) -> None:
        pass

    def test_send_email(self):
        ret = notification.send_by_channel('Hello, Title', 'This is a test notification', NOTIFY_CHANNEL_EMAIL, 'luna@equestria.org')
        self.assertTrue(ret)
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertEqual('Hello, Title', mail.outbox[-1].subject)

    def test_send_slack(self):
        ret = notification.send_by_channel('Hello, Title', 'This is a test notification', NOTIFY_CHANNEL_SLACK,
                                           'https://hooks.slack.com/services/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')
        self.assertTrue(ret)

    def test_send_unknown(self):
        ret = notification.send_by_channel('Hello, Title', 'This is a test notification', 'unknown', 'unknown url')
        self.assertFalse(ret)

    def test_check_and_get_pony(self):
        pony = check_and_get_pony(EXISTED_PONY_NAME,EXISTED_PONY_PASSCODE)
        self.assertIsNotNone(pony)
        pony = check_and_get_pony(EXISTED_PONY_NAME, 'wrong pass')
        self.assertIsNone(pony)
        pony = check_and_get_pony('wrong name', EXISTED_PONY_PASSCODE)
        self.assertIsNone(pony)


class ClientTest (TestCase):

    @classmethod
    def setUpTestData(cls):
        add_testing_pony()

    def setUp(self) -> None:
        self.client = Client()

    def test_index_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'luna')

    def test_add_pony(self):
        pony_name = 'dali'
        pony_passcode = 'hello'
        response = self.client.post(reverse('add_pony'),{
            'name': pony_name,
            'passcode': pony_passcode,
            'dark_minute': '5',
            'notify_channel': 'EMAIL',
            'notify_url': 'luna@equestria.org'
        })
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        self.assertEquals(response_json['code'], 0, response_json['msg'])
        self.assertIn('id', response_json['data'])
        pony = Pony.objects.get(name='dali')
        self.assertEqual(pony_name, pony.name)
        self.assertEqual(pony.passcode, hash_password(pony_passcode))
        self.assertEqual(Pony.STATUS_INIT, pony.status)
        self.assertEqual(5, pony.dark_minute)
        self.assertEqual('EMAIL', pony.notify_channel)
        self.assertEqual('luna@equestria.org', pony.notify_url)

    def test_say_hello(self):
        response = self.client.get(reverse('hello_pony'),{
            'name': EXISTED_PONY_NAME,
            'passcode': EXISTED_PONY_PASSCODE
        })
        response_json = response.json()
        self.assertEqual(200, response.status_code)
        self.assertEquals(0, response_json['code'])
        #  check pony
        pony = get_testing_pony()
        self.assertEqual(Pony.STATUS_NORMAL, pony.status)
        self.assertIsNotNone(pony.last_hi_time)
        self.assertTrue(20 > (now() - pony.last_hi_time).seconds >= 0)
        #  check history
        histories = History.objects.filter(pony_id=pony.id).order_by('-id')[:1]
        self.assertEqual(1, histories.count())
        history: History = histories[0]
        self.assertEqual(Pony.STATUS_INIT, history.previous_status)
        self.assertEqual(Pony.STATUS_NORMAL, history.current_status)
        self.assertTrue(20 > (now() - history.create_time).seconds >= 0)

    def test_get_pony(self):
        response = self.client.get(reverse('get_pony'), {
                                    'name': EXISTED_PONY_NAME,
                                    'passcode': EXISTED_PONY_PASSCODE
                                    })
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        self.assertEqual(0, response_json['code'])
        self.assertEqual(EXISTED_PONY_NAME, response_json['data']['name'])
        self.assertIn('id', response_json['data'])
        self.assertIn('status', response_json['data'])

    def test_change_pony(self):
        response = self.client.get(reverse('change_pony'),{
            'name': EXISTED_PONY_NAME,
            'passcode': EXISTED_PONY_PASSCODE,
            'dark_minute': 15,
            'notify_channel': NOTIFY_CHANNEL_EMAIL,
            'notify_url': 'luna2@equestria.org'
        })
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        self.assertEqual(0, response_json['code'])
        pony = get_testing_pony()
        self.assertEqual(15, pony.dark_minute)
        self.assertEqual(NOTIFY_CHANNEL_EMAIL, pony.notify_channel)
        self.assertEqual('luna2@equestria.org', pony.notify_url)

        response = self.client.get(reverse('change_pony'),{
            'name': EXISTED_PONY_NAME,
            'passcode': EXISTED_PONY_PASSCODE,
            'notify_channel': NOTIFY_CHANNEL_SLACK,
        })
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        self.assertEqual(1, response_json['code'])

    def test_remove_pony(self):
        response = self.client.get(reverse('remove_pony'), {
                                    'name': EXISTED_PONY_NAME,
                                    'passcode': EXISTED_PONY_PASSCODE
                                    })
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        self.assertEqual(0, response_json['code'])
        pony = get_testing_pony()
        self.assertIsNone(pony)