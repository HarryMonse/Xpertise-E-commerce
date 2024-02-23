import random
import datetime
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from django.contrib.auth import login,authenticate
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth import logout,login


from django.contrib import messages
from django.utils import timezone


from .models import *

# Create your views here.

def index(request):
    return render(request, "user_side/index.html")

def user_login(request):
    return render(request, "user_side/user_login.html")



def generate_otp():
    otp = str(random.randint(100000,999999))
    timestamp = str(timezone.now())
    return otp, timestamp



def user_signup(request):
    if request.user.is_authenticated:
        return redirect('user_index')

    if request.method == 'POST':
        username=request.POST.get('username')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        password=request.POST.get('password')
        cpassword=request.POST.get('cpassword')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request,'Username is already existing. Please choose a different Username.')
            return render(request, 'user_side/user_signup.html')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email is already existing. Please choose a different Email.')
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
            fail_silently=False
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
        

        if entered_otp == stored_otp:
            new_user=CustomUser(
                username=request.session['signup_details']['username'],
                email=request.session['signup_details']['email'],
                first_name=request.session['signup_details']['first_name'],
                last_name=request.session['signup_details']['last_name'],
                phone=request.session['signup_details']['phone'],
                password=request.session['signup_details']['password']
            )
            new_user.save()
            login(request, new_user)

            request.session.pop('signup_otp',None)
            request.session.pop('otp_timestamp', None)
            request.session.pop('signup_details',None)
            return redirect('index')
        else:
            messages.error(request,'Invalid OTP. Please try again.')

    expiration_time = datetime.fromisoformat(request.session.get('otp_timestamp')) + timedelta(minutes=1)
    remaining_time = max(timedelta(0), expiration_time - timezone.now())
    remaining_minutes, remaining_seconds = divmod(remaining_time.seconds, 60)

    return render(request, 'user_side/otp.html',{'remaining_minutes': remaining_minutes, 'remaining_seconds': remaining_seconds})



def resend_otp(request):
    if 'signup_details' in request.session:
        otp, timestamp = generate_otp()

        request.session['signup_otp'] = otp
        request.session['otp_timestamp'] = timestamp

        send_mail(
            'Resent OTP verification',
            f'Welcome to Xpertise. Your new OTP for signup is: {otp}',
            'xpertise.hm@gmail.com',
            [request.session['signup_details']['email']],
            fail_silently=True
        )
        messages.info(request, 'New OTP sent. Please check your email.')
        return redirect('enter_otp')
    else:
        messages.error(request, 'No signup session found.')
        return redirect('user_signup')
    

@cache_control(max_age=0, no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def user_logout(request):
    logout(request)
    return redirect('user_login')
    


@cache_control(max_age=0, no_cache=True, must_revalidate=True, no_store=True)
@never_cache  
def signin(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user = None

        print(user)
        if user is not None and user.check_password(password):
            if user.is_active:
                login(request,user)
                return redirect('index')
            else:
                messages.error(request, 'Your account is not active')
        else:
            messages.error(request, 'Invalid Username or Password')   
    return render(request, 'user_side/user_login.html')




def services(request, category_id=None,type_id=None):
    all_categories = category.objects.filter(is_deleted=False,is_blocked=False)
    selected_category = None
    selected_type = None
    services = None
    service_count = None
    types = Type.objects.filter(is_active=True)
    



                
    if 'category_id' in request.GET:
        category_id = request.GET['category_id']
        selected_category = get_object_or_404(category, id=category_id)
        services = Service.objects.filter(
            category=selected_category,
            is_available=True,
            is_deleted=False,
            type__is_active=True,
            category__is_deleted=False,
            category__is_blocked=False
        )
        service_count = services.count()

    elif 'type_id' in request.GET:
        type_id = request.GET['type_id']
        selected_type = get_object_or_404(Type, id=type_id)
        services = Service.objects.filter(
            type=selected_type,
            is_available=True,
            is_deleted=False,
            type__is_active=True,
            category__is_deleted=False,
            category__is_blocked=False
        )
        service_count = services.count()

    else:
        services = Service.objects.filter(is_available=True, is_deleted=False, type__is_active=True ,category__is_deleted=False,category__is_blocked=False)
        service_count = services.count()

   
    context = {
        'services': services,
        'service_count': service_count,
        'all_categories': all_categories,
        'selected_category': selected_category,
        # 'discount_offer':discount_offer,
        # "discounted_offer":discounted_offer,
        'selected_type': selected_type,
        'types': types,
        
        
    }

    return render(request, 'user_side/services.html', context)




def service_details(request, service_id, category_id):
    user=request.user
    service = Service.objects.get(id=service_id)
    images = ServiceImages.objects.filter(service=service)
    related_service=Service.objects.filter(category=service.category).exclude(id=service_id)[:4]
    provider_types = ServiceAttribute.objects.filter(service=service).distinct()


    if request.method=="POST":
        if user.is_authenticated:
            print("request entered ")
            colour=request.POST.get('provider_typeselect')
            qty=request.POST.get('quantity')
            service_colour=ProviderType.objects.get(provider_type_name=colour)
            services=ServiceAttribute.objects.get(service=service,provider_type=service_colour)
           
            print("Related Services:", related_service)
        else:
            return redirect('user_login')

    
    context={
        'service': service,
        'related_service': related_service,
        'provider_types' :provider_types,
        'images':images,
    }
    

    return render(request, 'user_side/service_details.html', context)