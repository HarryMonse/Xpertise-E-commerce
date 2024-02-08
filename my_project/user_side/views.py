import random
import datetime
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta

from django.contrib import messages
from django.utils import timezone


from .models import User

# Create your views here.

def index(request):
    return render(request, "user_side/index.html")

def user_login(request):
    return render(request, "user_side/user_login.html")



def generate_otp():
    otp = str(random.randomint(100000,999999))
    timestamp = str(timezone.now())
    return otp, timestamp



def user_signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username=request.POST.get('username')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        password=request.POST.get('password')
        cpassword=request.POST.get('cpassword')

        if User.objects.filter(username=username).exists():
            messages.error(request,'Username is already existing. Please choose a different username.')
            return render(request, 'user_side/user_signup.html')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already existing. Please choose a different email.')
            return render(request, 'user_side/user_signup.html')
        elif cpassword != password:
            messages.error(request, 'Mismatch in password')
            return render(request, 'user_side/user_signup.html')
        
        otp, timestamp = generate_otp()
        request.session['signup_otp'] = otp
        request.session['otp_timestamp'] = timestamp

        send_mail(
            'OTP Verification',
            f'Welcome to Xpertise. Your OTP is : {otp}',
            'xpertise.hm@gmail.com',
            [email],
            fail_silently=True
        )

        request.session['signup_details']={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'password': make_password(password),
        }
        return redirect(enter_otp)
    return render(request, "user_side/user_signup.html")



def enter_otp(request):
    if request.method == 'POST':
        entered_otp=request.POST.get('otp')
        stored_otp=request.session.get('signup_otp')
        timestamp_str = request.session.get('otp_timestamp')

        expiration_time = datetime.fromisoformat(timestamp_str) + timedelta(minutes=1)
        current_time = timezone.now()

        if current_time > expiration_time:
            messages.error(request, 'OTP has expired. Please request a new one.')
            return render(request, 'user_side/otp.html')


    return render(request, 'user_side/otp.html',{'remaining_minutes': remaining_minutes, 'remaining_seconds': remaining_seconds})