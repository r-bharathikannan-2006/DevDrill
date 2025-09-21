from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_template, name='search_template'),
    path('player/<str:video_id>/', views.open_player, name='open_player'),
]