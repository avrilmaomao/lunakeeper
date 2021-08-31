import logging

import django.core.mail as mail
from typing import Tuple
from django.utils.timezone import now

from ..utils import send_json_request
from ..consts import NOTIFY_CHANNEL_SLACK, NOTIFY_CHANNEL_EMAIL
from ..models import Pony

STATUS_NAME = {
    Pony.STATUS_INIT: 'Just Created',
    Pony.STATUS_NORMAL: 'Normal',
    Pony.STATUS_MISSING: 'Missing'
}


def send_status_change_notification(pony: Pony, previous_status: int, after_status: int):
    if previous_status == after_status:
        return
    title, content = generate_status_change_message(pony, previous_status, after_status)
    send_by_channel(title, content, pony.notify_channel, pony.notify_url)


def generate_status_change_message(pony: Pony, previous_status: int, after_status: int) -> Tuple[str, str]:
    title = f"Your pony {pony.name} just changed it's status"
    if previous_status == Pony.STATUS_INIT and after_status == Pony.STATUS_NORMAL:
        title = f"Your pony {pony.name}'s greeting was received for the first time!"
    if previous_status == Pony.STATUS_NORMAL and after_status == Pony.STATUS_MISSING:
        title = f"Your pony {pony.name} was missing"
    if previous_status == Pony.STATUS_MISSING and after_status == Pony.STATUS_NORMAL:
        title = f"Your pony {pony.name} has come back"
    content = f"Status Change: {STATUS_NAME[previous_status]} --> {STATUS_NAME[after_status]}\nswitch time: {now()}"
    return title, content


def send_by_channel(title:str, content: str, channel: str, url: str):
    if channel == NOTIFY_CHANNEL_EMAIL:
        return send_email(title, content, url)
    elif channel == NOTIFY_CHANNEL_SLACK:
        return send_slack_notification(title, content, url)
    else:
        logging.error("unknown channel:%s", locals())
        return False


def send_email(title: str, content: str, address: str,) -> bool:
    try:
        return mail.send_mail(title, content, None, recipient_list=[address]) == 1
    except BaseException as e:
        logging.error("send email encountered exception", exc_info=e)
        return False


def send_slack_notification(title: str, content: str, url: str) ->bool:
    content = title + "\n" + content
    params = {
        "text": content
    }
    try:
        response = send_json_request(url, params, False)
        if response == "ok":
            logging.info("send slack successfully")
            return True
        logging.error("sending slack notifications response error:%s", response)
        return False
    except BaseException as e:
        logging.error("error occurred while sending slack notifications", exc_info=e)
        return False
