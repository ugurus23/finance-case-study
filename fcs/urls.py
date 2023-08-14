# example/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path('', views.index),
    path('cik/<slug:slug>/', views.manager),
    path('cusip/<slug:slug>/', views.issuer),
]