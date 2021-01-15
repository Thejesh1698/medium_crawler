from django.urls import path

from . import views

urlpatterns = [
    path('', views.admin, name='admin'),
    path('main_crawler/', views.main_crawler, name='main_crawler'),
]