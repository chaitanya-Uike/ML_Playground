from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home, name='home'),
    path('save-config/<str:session>/', views.saveConfig, name='saveConfig'),
    path('network/<str:session>/', views.network, name="network"),
    path('train/<str:session>/', views.train, name="train"),
    path('close-session/', views.close, name="close"),
    path('head/<str:session>/', views.head, name="head"),
    path('drop/<str:session>/', views.drop, name="drop"),
    path('encode/<str:session>/', views.encode, name="encode"),
]

