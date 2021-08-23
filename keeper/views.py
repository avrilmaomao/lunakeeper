from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpRequest
from django.forms import IntegerField,EmailField, URLField,model_to_dict
from django.utils.timezone import now


from .forms import *
from .consts import *
from .models import Pony
from .utils import hash_password
# Create your views here.

def index(request : HttpRequest):
    context = {
        'domain': request.get_host()
    }
    return render(request, 'keeper/index.html', context)


def add_pony(request: HttpRequest):
    try:
        query_params = get_query_param(request)
        name = NameField().clean(query_params.get('name'))
        passcode = PasscodeField().clean(query_params.get('passcode'))
        dark_minute = IntegerField(min_value=5, max_value= 43200).clean(query_params.get('dark_minute'))
        notify_channel = NotifyChannelField().clean(query_params.get('notify_channel'))
        if notify_channel == NOTIFY_CHANNEL_EMAIL:
            notify_url = EmailField().clean(query_params.get('notify_url'))
        else:
            notify_url = URLField().clean(query_params.get('notify_url'))
    except ValidationError as e:
        return error_response(e.messages[0])
    #  check whether name exists
    num_of_pony = Pony.objects.filter(name__exact=name).count()
    if num_of_pony > 0:
        return error_response('pony with same name already exists')
    pony = Pony(name=name, passcode=hash_password(passcode), dark_minute = dark_minute, notify_channel=notify_channel,
                notify_url=notify_url, create_time= now(), status= Pony.STATUS_INIT)
    pony.save()
    # 测试通知 @todo
    return succ_response({'id': pony.id, 'name': pony.name},
                         msg="check your notification channel whether you've received a creation message")


def hello_pony(request):
    return JsonResponse()

def get_pony(request):
    return JsonResponse()


def change_pony(request):
    return JsonResponse()

def remove_pony(request):
    return JsonResponse()


def error_response(message: str):
    return JsonResponse({'code': 0, 'msg': message})


def succ_response(data, msg=''):
    return JsonResponse({'code': 1, 'data': data, 'msg': msg})


def get_query_param(request: HttpRequest):
    if request.method == 'GET':
        query_params = request.GET
    elif request.method == 'POST':
        query_params = request.POST
    else:
        raise Exception('Unsupported HTTP method')
    return query_params
