import logging
import typing

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.forms import IntegerField, EmailField, model_to_dict
from django.utils.timezone import now

from .forms import *
from .consts import *
from .models import Pony, History
from .utils import hash_password, run_in_background
from .services import notification


# Create your views here.

def index(request: HttpRequest):
    context = {
        'domain': request.get_host()
    }
    return render(request, 'keeper/index.html', context)


def add_pony(request: HttpRequest):
    try:
        query_params = get_query_param(request)
        name = NameField().clean(query_params.get('name'))
        passcode = PasscodeField().clean(query_params.get('passcode'))
        dark_minute = IntegerField(min_value=5, max_value=43200).clean(query_params.get('dark_minute'))
        notify_channel = NotifyChannelField().clean(query_params.get('notify_channel'))
        if notify_channel == NOTIFY_CHANNEL_EMAIL:
            notify_url = EmailField().clean(query_params.get('notify_url'))
        else:
            notify_url = NotifyWebUrlField().clean(query_params.get('notify_url'))
    except ValidationError as e:
        return error_response(e.messages[0])
    #  check whether name exists
    num_of_pony = Pony.objects.filter(name__exact=name).count()
    if num_of_pony > 0:
        return error_response('pony with same name already exists')
    pony = Pony(name=name, passcode=hash_password(passcode), dark_minute=dark_minute, notify_channel=notify_channel,
                notify_url=notify_url, create_time=now(), status=Pony.STATUS_INIT)
    pony.save()
    run_in_background(notification.send_by_channel, 'pony created', f'Your pony {name} has been created',
                      notify_channel, notify_url)
    return succ_response({'id': pony.id, 'name': pony.name},
                         msg="check your notification channel whether you've received a creation message")


def hi_pony(request):
    pony = check_pony_or_response(request)
    if type(pony) != Pony:
        return pony

    previous_status = pony.status
    after_status = Pony.STATUS_NORMAL

    pony.status = after_status
    pony.last_hi_time = now()
    pony.save()

    if previous_status != after_status:
        history = History()
        history.pony_id = pony.id
        history.previous_status = previous_status
        history.current_status = after_status
        history.create_time = now()
        history.save()
        #  send notification
        run_in_background(notification.send_status_change_notification, pony, previous_status, after_status)
        logging.info("Pony status change:%s,%d,%d", pony.name, previous_status, after_status)

    return succ_response({'previous': previous_status, 'current': after_status})


def get_pony(request):
    pony = check_pony_or_response(request)
    if type(pony) != Pony:
        return pony
    return succ_response(model_to_dict(pony))


def change_pony(request):

    pony = check_pony_or_response(request)
    if type(pony) != Pony:
        return pony
    dark_minute = pony.dark_minute
    notify_channel = pony.notify_channel
    notify_url = pony.notify_url

    query_params = get_query_param(request)
    try:
        if 'dark_minute' in query_params:
            dark_minute = IntegerField(min_value=5, max_value=43200).clean(query_params.get('dark_minute'))
        if 'notify_channel' in query_params:
            notify_channel = NotifyChannelField().clean(query_params.get('notify_channel'))
        if 'notify_url' in query_params:
            notify_url = query_params.get('notify_url')
        if notify_channel == NOTIFY_CHANNEL_EMAIL:
            notify_url = EmailField().clean(notify_url)
        else:
            notify_url = NotifyWebUrlField().clean(notify_url)
    except ValidationError as e:
        return error_response(e.messages[0])

    pony.dark_minute = dark_minute
    need_notification: bool = False
    if pony.notify_url != notify_url or pony.notify_channel != notify_channel:
        pony.notify_channel = notify_channel
        pony.notify_url = notify_url
        need_notification = True
    pony.save()

    if need_notification:
        run_in_background(notification.send_by_channel,
                          "Pony Updated",
                          f"Your pony {pony.name} has been updated",
                          notify_channel, notify_url)

    return succ_response({'name': pony.name, 'dark_minute': dark_minute,
                          'notify_channel': notify_channel,
                          'notify_url': notify_url
                          })


def remove_pony(request):
    pony = check_pony_or_response(request)
    if type(pony) != Pony:
        return pony
    pony.delete()
    return succ_response(None)


def error_response(message: str, code=RESPONSE_CODE_FAIL):
    return JsonResponse({'code': code, 'msg': message})


def succ_response(data, msg=''):
    return JsonResponse({'code': RESPONSE_CODE_SUCC, 'data': data, 'msg': msg})


def get_query_param(request: HttpRequest):
    if request.method == 'GET':
        query_params = request.GET
    elif request.method == 'POST':
        query_params = request.POST
    else:
        raise Exception('Unsupported HTTP method')
    return query_params


def check_pony_or_response(request):
    try:
        query_params = get_query_param(request)
        name = NameField().clean(query_params.get('name'))
        passcode = PasscodeField().clean(query_params.get('passcode'))
    except ValidationError as e:
        return error_response(e.messages[0])
    pony = check_and_get_pony(name, passcode)
    if pony is None:
        return error_response('failed to find pony,check your name and passcode')
    return pony


def check_and_get_pony(name: str, passcode: str) -> typing.Optional[Pony]:
    passcode = hash_password(passcode)
    try:
        return Pony.objects.get(name=name, passcode=passcode)
    except Pony.DoesNotExist as e:
        logging.warning("failed to find pony:%s", name)
        return None
    except BaseException as e:
        logging.error("check pony exception encountered", exc_info=e)
        return None



