from django.urls import path
from admin_side import views


urlpatterns = [
    path('admin_login', views.admin_login , name ='admin_login'),
]