import datetime
import typing
from io import StringIO

from django.test import TestCase,Client
from django.urls import reverse
from django.utils.timezone import now
from django.core import mail
from django.core.management import call_command

from .services import notification
from .models import Pony,History
from .consts import NOTIFY_CHANNEL_EMAIL,NOTIFY_CHANNEL_SLACK
from .views import check_and_get_pony
from .utils import hash_password


# Create your tests here.

NEW_TESTING_PONY_NAME = 'dali01'
TESTING_PONY_PASSCODE = 'pass001'
MISSING_PONY_NAME = 'dali02'


def add_testing_pony(name = NEW_TESTING_PONY_NAME, last_hi_time = None, status = Pony.STATUS_INIT):
    if get_testing_pony(name) is not None:
        print("Testing pony already added")
        return
    pony = Pony(
        name=name,
        passcode=hash_password(TESTING_PONY_PASSCODE),
        dark_minute=5,
        notify_channel=NOTIFY_CHANNEL_EMAIL,
        notify_url='luna@equestria.org',
        create_time=now(),
        status= status
    )
    if last_hi_time is not None:
        pony.last_hi_time = last_hi_time
    pony.save()
    print("Testing Pony added")


def get_testing_pony(name = NEW_TESTING_PONY_NAME) -> typing.Optional[Pony]:
    try:
        return Pony.objects.get(name=name)
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

    def test_send_unknown(self):
        ret = notification.send_by_channel('Hello, Title', 'This is a test notification', 'unknown', 'unknown url')
        self.assertFalse(ret)

    def test_check_and_get_pony(self):
        pony = check_and_get_pony(NEW_TESTING_PONY_NAME, TESTING_PONY_PASSCODE)
        self.assertIsNotNone(pony)
        pony = check_and_get_pony(NEW_TESTING_PONY_NAME, 'wrong pass')
        self.assertIsNone(pony)
        pony = check_and_get_pony('wrong name', TESTING_PONY_PASSCODE)
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
        self.assertContains(response, 'Luna')

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

    def test_say_hi(self):
        response = self.client.get(reverse('hi_pony'),{
            'name': NEW_TESTING_PONY_NAME,
            'passcode': TESTING_PONY_PASSCODE
        })
        response_json = response.json()
        self.assertEqual(200, response.status_code)
        self.assertEquals(0, response_json['code'])
        #  check pony
        pony = get_testing_pony()
        self.assertEqual(Pony.STATUS_NORMAL, pony.status)
        self.assertIsNotNone(pony.last_hi_time)
        self.assertTrue(20 > (now() - pony.last_hi_time).total_seconds() >= 0)
        #  check history
        histories = History.objects.filter(pony_id=pony.id).order_by('-id')[:1]
        self.assertEqual(1, histories.count())
        history: History = histories[0]
        self.assertEqual(Pony.STATUS_INIT, history.previous_status)
        self.assertEqual(Pony.STATUS_NORMAL, history.current_status)
        self.assertTrue(20 > (now() - history.create_time).total_seconds() >= 0)

    def test_get_pony(self):
        response = self.client.get(reverse('get_pony'), {
                                    'name': NEW_TESTING_PONY_NAME,
                                    'passcode': TESTING_PONY_PASSCODE
                                    })
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        self.assertEqual(0, response_json['code'])
        self.assertEqual(NEW_TESTING_PONY_NAME, response_json['data']['name'])
        self.assertIn('id', response_json['data'])
        self.assertIn('status', response_json['data'])

    def test_change_pony(self):
        response = self.client.get(reverse('change_pony'),{
            'name': NEW_TESTING_PONY_NAME,
            'passcode': TESTING_PONY_PASSCODE,
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
            'name': NEW_TESTING_PONY_NAME,
            'passcode': TESTING_PONY_PASSCODE,
            'notify_channel': NOTIFY_CHANNEL_SLACK,
        })
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        self.assertEqual(1, response_json['code'])

    def test_remove_pony(self):
        response = self.client.get(reverse('remove_pony'), {
                                    'name': NEW_TESTING_PONY_NAME,
                                    'passcode': TESTING_PONY_PASSCODE
                                    })
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        self.assertEqual(0, response_json['code'])
        pony = get_testing_pony()
        self.assertIsNone(pony)

    def test_check_pony_command(self):
        add_testing_pony(name=MISSING_PONY_NAME, last_hi_time=now() - datetime.timedelta(days=1), status=Pony.STATUS_NORMAL)
        out = StringIO()
        call_command('checkpony', stdout=out)
        self.assertIn('start checking', out.getvalue())
        self.assertIn('finished checking', out.getvalue())

        pony = get_testing_pony(NEW_TESTING_PONY_NAME)
        self.assertEquals(Pony.STATUS_INIT, pony.status)

        missing_pony = get_testing_pony(MISSING_PONY_NAME)
        self.assertEqual(Pony.STATUS_MISSING, missing_pony.status)
        history = History.objects.order_by('-id').filter(pony_id=missing_pony.id)[0]
        self.assertIsNotNone(history)
        self.assertEquals(Pony.STATUS_NORMAL, history.previous_status)
        self.assertEquals(Pony.STATUS_MISSING, history.current_status)
        has_missing_email: bool = False
        missing_email_title = notification.generate_status_change_message(missing_pony, Pony.STATUS_NORMAL, Pony.STATUS_MISSING)[0]
        for message in mail.outbox:
            if missing_email_title == message.subject:
                has_missing_email = True
                break
        self.assertTrue(has_missing_email)



