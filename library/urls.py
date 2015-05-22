from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^authorise$', views.authorise, name='authorise'),
    url(r'^callback$', views.callback, name='callback'),
]