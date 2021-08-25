from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add_pony, name='add_pony'),
    path('hello', views.hello_pony, name='hello_pony'),
    path('get', views.get_pony, name = 'get_pony'),
    path('change', views.change_pony, name = 'change_pony'),
    path('remove', views.remove_pony, name = 'remove_pony')
]