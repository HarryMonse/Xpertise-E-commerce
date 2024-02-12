from django.urls import path
from user_side import views


urlpatterns = [
    path('user_login/',views.signin,name='user_login'),
    path('user_logout/',views.user_logout,name='user_logout'),
    path("", views.index, name="index"),
    path('user_login/', views.user_login, name='user_login'),
    path('user_signup/', views.user_signup, name='user_signup'),
    path('enter_otp/',views.enter_otp,name='enter_otp'),
    path('resend_otp/',views.resend_otp,name='resend_otp'),
    path('services/', views.services, name='services'),





]