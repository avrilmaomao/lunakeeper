from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpRequest
# Create your views here.

def index(request : HttpRequest):
    context = {
        'domain': request.get_host()
    }
    return render(request, 'keeper/index.html', context)



def add_pony(request):

    return JsonResponse()


def hello_pony(request):
    return JsonResponse()

def get_pony(request):
    return JsonResponse()


def change_pony(request):
    return JsonResponse()

def remove_pony(request):
    return JsonResponse()