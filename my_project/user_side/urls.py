from django.urls import path
from user_side import views


urlpatterns = [
    path("", views.index, name="index"),
    path('user_login/', views.user_login, name='user_login'),
    path('user_signup/', views.user_signup, name='user_signup'),



]