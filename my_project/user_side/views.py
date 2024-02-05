from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, "user_side/index.html")

def user_home(request):
    return render(request, "user_side/user_home.html")

def user_login(request):
    return render(request, "user_side/user_login.html")

