from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pony/add', views.add_pony, name='add_pony'),
    path('pony/hi', views.hi_pony, name='hi_pony'),
    path('pony/get', views.get_pony, name='get_pony'),
    path('pony/change', views.change_pony, name='change_pony'),
    path('pony/remove', views.remove_pony, name='remove_pony')
]