from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.preview_excel_data, name='upload'),
    path('confirm/', views.confirm_push, name='confirm_push'),
]