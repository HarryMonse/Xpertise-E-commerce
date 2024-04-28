import random
import datetime
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from django.contrib.auth import login,authenticate
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.cache import never_cache, cache_control
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout,login
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.db.models import OuterRef, Subquery
from admin_side.models import *
from payment.forms import AddressForm
from django.db.models import Sum
from django.contrib import messages
from django.utils import timezone
from .models import *
from payment.models import *


# Create your views here.


@cache_control(max_age=0,no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def index(request):
    services = Service.objects.filter(featured=True,category__is_deleted=False,category__is_blocked=False).order_by('-id').distinct()
    banners =Banner.objects.filter(is_active=True)
    if request.session.get('order_placed', False):
        del request.session['order_placed']
        messages.success(request, 'Order placed successfully!')
        return redirect('index') 
    
    try:
        discount_offer = ServiceOffer.objects.get(active=True)
    except ServiceOffer.DoesNotExist:
        discount_offer = None
    if discount_offer:
        current_date = timezone.now()
        if current_date > discount_offer.end_date or current_date < discount_offer.start_date:
            discount_offer.active = False
            discount_offer.save()
    try:
        
        discounted_offer = CategoryOffer.objects.filter(active=True)
    except ServiceOffer.DoesNotExist:
        discounted_offer = None
    if discounted_offer:
        for dis in discounted_offer:
            services_with_discount = Service.objects.filter(category=dis.category, is_available=True)
            current_date = timezone.now()
            if current_date > dis.end_date or current_date < dis.start_date:
                dis.active = False
                dis.save()
    context = {
        'services': services,  
        "discount_offer":discount_offer,
        "discounted_offer":discounted_offer,
        'banners':banners,
    }
    return render(request, 'user_side/index.html',context)

def user_login(request):
    return render(request, "user_side/user_login.html")


def generate_otp():
    otp = str(random.randint(100000,999999))
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


def search(request):
    q=request.GET['q']
    try:
        discount_offer = ServiceOffer.objects.get(active=True)
    except ServiceOffer.DoesNotExist:
        discount_offer = None
    if discount_offer:
        current_date = timezone.now()
        if current_date > discount_offer.end_date or current_date < discount_offer.start_date:
            discount_offer.active = False
            discount_offer.save()
    try:
        
        discounted_offer = CategoryOffer.objects.filter(active=True)
    except ServiceOffer.DoesNotExist:
        discounted_offer = None
    if discounted_offer:
        for dis in discounted_offer:
            services_with_discount = Service.objects.filter(category=dis.category, is_available=True)
            current_date = timezone.now()
            if current_date > dis.end_date or current_date < dis.start_date:
                dis.active = False
                dis.save()
    data = Service.objects.filter(service_name__icontains=q).order_by('-id')
    return render(request,'user_side/search.html',{'data':data,"discount_offer":discount_offer,"discounted_offer":discounted_offer,})


def services(request, category_id=None,type_id=None):
    all_categories = category.objects.filter(is_deleted=False,is_blocked=False)
    selected_category = None
    selected_type = None
    services = None
    service_count = None
    types = Type.objects.filter(is_active=True)

    try:
        discount_offer = ServiceOffer.objects.get(active=True)
    except ServiceOffer.DoesNotExist:
        discount_offer = None
        
    try:
        
        discounted_offer = CategoryOffer.objects.filter(active=True)
    except ServiceOffer.DoesNotExist:
        discounted_offer = None
    if discounted_offer:
        for dis in discounted_offer:
            services_with_discount = Service.objects.filter(category=dis.category, is_available=True)
            current_date = timezone.now()
            if current_date > dis.end_date:
                dis.active = False
                dis.save()
                
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
        'discount_offer':discount_offer,
        "discounted_offer":discounted_offer,
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

    try:   
        discount_offer = ServiceOffer.objects.get(active=True)
    except ServiceOffer.DoesNotExist:
        discount_offer = None
                        
    try:
        discounted_offer = CategoryOffer.objects.filter(active=True)
    except ServiceOffer.DoesNotExist:
        discounted_offer = None
    if discounted_offer:
        for dis in discounted_offer:
            products_with_discount = Service.objects.filter(category=dis.category, is_available=True)
            current_date = timezone.now()
            if current_date > dis.end_date:
                dis.active = False
                dis.save()

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
        "discount_offer":discount_offer,
        "discounted_offer":discounted_offer,
    }
    
    return render(request, 'user_side/service_details.html', context)


@login_required(login_url='user_login')
def add_to_cart(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login to access cart')
        return redirect('user_login')

    user = request.user
    
    if request.method == 'POST':
        service_id = request.POST.get('item_id')
        provider_type_name = request.POST.get('service_provider_type')
        qty = int(request.POST.get('quantity'))  

        try:
            provider_type = ProviderType.objects.get(provider_type_name=provider_type_name)
            service = ServiceAttribute.objects.get(service=service_id, provider_type=provider_type)
        except (ProviderType.DoesNotExist, ServiceAttribute.DoesNotExist):
            messages.error(request, 'Invalid service or provider_type.')
            return JsonResponse({'status': 'error', 'message': 'Invalid service or provider_type.'}, status=400)
        
        print(f"Selected Service ID: {service_id}")
        print(f"Selected ProviderType: {provider_type_name}")
        print(f"Selected Quantity: {qty}")
        if qty > service.availability:
            messages.error(request, f"Insufficient availability. Only {service.availability} available.")
            response_data = {
            'status': 'error',
            'message': f"Insufficient availability. Only {service.availability} available."
            
            }
            return JsonResponse(response_data)

        try:
            cart_item = CartItem.objects.get(service=service, user=user, is_deleted=False)
            available_availability = service.availability - cart_item.quantity
            if qty > available_availability:
                messages.error(request, f"Insufficient availability. Only {available_availability} available.")
                response_data = {
                    'status': 'error',
                    'message': f"Insufficient availability. Only {available_availability} available."
                    
                    }
                return JsonResponse(response_data)

            cart_item.quantity += qty
            cart_item.total = service.price * cart_item.quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            item, created = CartItem.objects.get_or_create(user=user, service=service, defaults={'is_deleted': False})
            item.quantity = qty
            item.total = service.price * qty
            item.save()

        cart_count = CartItem.objects.filter(user=request.user, is_deleted=False).count()

        response_data = {
            'status': 'success',
            'message': 'Service added to cart successfully',
            'cart_count': cart_count
        }
        return JsonResponse(response_data)
    else:
        print('Invalid request or not AJAX') 
        return JsonResponse({'status': 'error', 'message': 'Invalid request or not AJAX'}, status=400)


@login_required(login_url='user_login')  
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)

def cart_list(request):
    user = request.user
    items = CartItem.objects.filter(user=user, is_deleted=False)
    coupons = Coupon.objects.all()
    ct = items.count()

    total_without_discount = items.aggregate(total_sum=Sum('total'))['total_sum'] or 0

    discounts = 0

    applied_coupon_id = request.session.get('applied_coupon_id')

    if request.session.get('order_placed', False):
        del request.session['order_placed']
        messages.success(request, 'Order placed successfully!')
        return redirect('index')  

    if applied_coupon_id:
        try:
            applied_coupon = Coupon.objects.get(id=applied_coupon_id, active=True,
                                                active_date__lte=timezone.now(), expiry_date__gte=timezone.now())
            discounts = (total_without_discount * applied_coupon.discount) / 100
        except Coupon.DoesNotExist:

            request.session.pop('applied_coupon_id', None)

    if request.method == "POST":
        if 'apply_coupon' in request.POST:
            coupon_code = request.POST.get('coupon_code')
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True, active_date__lte=timezone.now(),
                                            expiry_date__gte=timezone.now())

                discounts = (total_without_discount * coupon.discount) / 100
                items.update(coupon=coupon)

                request.session['applied_coupon_id'] = coupon.id

                messages.success(request, 'Coupon applied successfully!')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid or expired coupon code')

        elif 'remove_coupon' in request.POST:

            request.session.pop('applied_coupon_id', None)

            total_without_discount = items.aggregate(total_sum=Sum('total'))['total_sum'] or 0
            discounts = 0

            applied_coupon_id = request.session.get('applied_coupon_id')
            if applied_coupon_id:
                try:
                    applied_coupon = Coupon.objects.get(id=applied_coupon_id, active=True,
                                                        active_date__lte=timezone.now(), expiry_date__gte=timezone.now())
                    discounts = (total_without_discount * applied_coupon.discount) / 100
                except Coupon.DoesNotExist:
                    request.session.pop('applied_coupon_id', None)

            items.update(coupon=None)

            total_after_discount = total_without_discount - discounts
            data = {
                'success': True,
                'totals': total_without_discount,
                'discounts': discounts,
                'total': total_after_discount,
            }

            messages.success(request, 'Coupon removed successfully!')
                    
    total_after_discount = total_without_discount - discounts

    context = {
        'items': items,
        'totals': total_without_discount,
        'total': total_after_discount,
        'ct': ct,
        'coupons': coupons,
        'discounts': discounts,
    }

    request.session['totals'] = total_without_discount
    request.session['total'] = total_after_discount
    request.session['discounts'] = discounts

    return render(request, 'user_side/cart.html', context)


@login_required(login_url='user_login')
def qty_update(request):
    user = request.user
    item_id = request.GET.get('item_id')
    new_quantity = int(request.GET.get('new_quantity'))

    cart_item = get_object_or_404(CartItem, id=item_id)
    now = timezone.now()

    if new_quantity > cart_item.service.availability:
        return JsonResponse({'error': 'Insufficient availability.', 'success': False}, status=400)

    cart_item.quantity = new_quantity
    cart_item.total = cart_item.service.price * new_quantity
    cart_item.save()

    total_without_discount = CartItem.objects.filter(user=user, is_deleted=False).aggregate(total_sum=Sum('total'))['total_sum'] or 0

    discounts = 0
    applied_coupon_id = request.session.get('applied_coupon_id')
    if applied_coupon_id:
        try:
            applied_coupon = Coupon.objects.get(id=applied_coupon_id, active=True,
                                                active_date__lte=timezone.now(), expiry_date__gte=timezone.now())
            discounts = (total_without_discount * applied_coupon.discount) / 100
        except Coupon.DoesNotExist:
            request.session.pop('applied_coupon_id', None)

    total_after_discount = total_without_discount - discounts

    response_data = {
        'new_qty': new_quantity,
        'new_price': cart_item.total,
        'totals': total_without_discount,
        'discounts': discounts,
        'total': total_without_discount
    }
    return JsonResponse(response_data)


@login_required(login_url='user_login')
def delete_cart_item(request):
    user = request.user
    item_id = request.GET.get('item_id')

    try:
        cart_item = CartItem.objects.get(id=item_id, user=user)
        cart_item.delete()

        cart_items = CartItem.objects.filter(user=user, is_deleted=False)
        totals = cart_items.aggregate(total_sum=Sum('total'))['total_sum'] or 0

        applied_coupon_id = request.session.get('applied_coupon_id')
        discounts = 0
        if applied_coupon_id:
            try:
                applied_coupon = Coupon.objects.get(id=applied_coupon_id, active=True,
                                                    active_date__lte=timezone.now(), expiry_date__gte=timezone.now())
                discounts = (totals * applied_coupon.discount) / 100
            except Coupon.DoesNotExist:
                request.session.pop('applied_coupon_id', None)

        cart_total = totals - discounts

        cart_count = cart_items.count()
        is_cart_empty = cart_items.count() == 0

        return JsonResponse({
            'success': True,
            'totals': totals,
            'discounts': discounts,
            'total': cart_total,
            'is_cart_empty': is_cart_empty,
            'cart_count': cart_count
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found in the cart'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@cache_control(max_age=0,no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')

def user_account(request):
    user_address = Address.objects.filter(users=request.user)
    
    order_history = CartOrder.objects.filter(user=request.user).order_by('-id').annotate(service_name=Subquery(
        ServiceOrder.objects.filter(order=OuterRef('pk')).order_by('id').values('service__service_name')[:1]
    ),
    service_image=Subquery(
        ServiceOrder.objects.filter(order=OuterRef('pk')).order_by('id').values('service__serviceattribute__image')[:1]
    ))
    order_items = ServiceOrder.objects.filter(user=request.user)
    for order in order_history:
        print(order.service_image)
    
    wallet, created = Wallet.objects.get_or_create(user=request.user, defaults={'balance': 0})
    
    wallethistory = WalletHistory.objects.filter(wallet=wallet)
    context={
         'user_address':user_address,
         'user_data' :request.user,
         'order_history': order_history,
         'order_items':order_items,
         'wallet':wallet,
         'wallethistory':wallethistory,
     }
    return render(request, 'user_side/user_account.html',context)


def add_address(request):
    if request.method=='POST':
        form = AddressForm(request.POST,request.FILES)
        if form.is_valid():
            address=form.save(commit=False)
            address.users = request.user
            address.save()
            return redirect('user_account')
    else:
        form=AddressForm()
    context={
        'form':form
    }
    return render(request, 'user_side/add_address.html',context)


@login_required(login_url='user_login')
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, users=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.instance.users = request.user
            form.save()
            return redirect('user_account')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'user_side/edit_address.html', {'form': form, 'address': address})


@login_required(login_url='user_login')
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, users=request.user)
    
    if request.method == 'POST':
        address.delete()
        return redirect('user_account')
    
    return render(request, 'user_side/delete_address.html', {'address': address})


@login_required(login_url='user_login')
def order_items(request, order_number):
    order = get_object_or_404(CartOrder, id=order_number)
    product_orders = ServiceOrder.objects.filter(order=order)
    for item in product_orders:
        item.subtotal = item.service_price * item.quantity
    context = {
        'order': order,
        'product_orders': product_orders,
        'order_total': sum(item.subtotal for item in product_orders),
    }

    return render(request, 'user_side/user_order_history.html', context)


@login_required(login_url='user_login')
def cancell(request,order_number):
    try:
        order = CartOrder.objects.get(id=order_number)
        wallet = Wallet.objects.get(user=request.user)

        if order.payment.payment_method == 'COD' or order.payment.payment_method == 'Razorpay':
            wallet.balance += order.order_total
            wallet.save()
            WalletHistory.objects.create(
                        wallet=wallet,
                        type='Credited',
                        amount=order.order_total,
                        reason='Item cancelation'
                        )

            refunded_message = f'Amount of {order.order_total} refunded successfully to your wallet.'
            messages.success(request, refunded_message)
    
            for service_order in order.serviceorder_set.all():
                service_attribute = service_order.variations
                service_attribute.availability += service_order.quantity
                service_attribute.save()

        order.status = 'Cancelled'
        order.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    except Exception as e:
        print(e)
       
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='user_login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        print(f'Entered password: {current_password}')
        print(f'Stored password: {request.user.password}')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Incorrect current password. Please try again.')
            return redirect('change_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New password and confirmation do not match. Please try again.')
            return redirect('change_password')

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(request, request.user)

        messages.success(request, 'Your password was successfully updated!')
        logout(request)
        return redirect('user_logout') 

    return render(request, 'user_side/change_password.html')


def add_wishlist(request, service_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login to access wishlist')
        return redirect('user_login')
    else:
        try:
            wishlist_item = WishlistItem.objects.get(user=request.user, service_id=service_id)
            messages.info(request, 'Service is already in your wishlist')
        except WishlistItem.DoesNotExist:
            WishlistItem.objects.create(user=request.user, service_id=service_id)
            messages.success(request, 'Service added to your wishlist successfully')
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def wishlist(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login to access wishlist')
        return redirect('user_login')
    else:
        context = {}
        try:
            wishlist_items = WishlistItem.objects.filter(user=request.user)
            context = {
                'wishlist_items': wishlist_items
            }
        except WishlistItem.DoesNotExist:
            pass
    return render(request, 'user_side/wishlist.html', context)


def delete_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id, user=request.user)
    wishlist_item.delete()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def filter_service(request):    
    try:
        min_price= request.GET['min_price']
        max_price= request.GET['max_price'] 

        services = Service.objects.filter(is_available=True,category__is_deleted=False,category__is_blocked=False, serviceattribute__is_deleted=False).order_by('-id').distinct()
        try:
            discount_offer = ServiceOffer.objects.get(active=True)
        except ServiceOffer.DoesNotExist:
            discount_offer = None
            
        try:
            
            discounted_offer = CategoryOffer.objects.filter(active=True)
        except ServiceOffer.DoesNotExist:
            discounted_offer = None
        if discounted_offer:
            for dis in discounted_offer:
                services_with_discount = Service.objects.filter(category=dis.category, is_available=True)
                current_date = timezone.now()
                if current_date > dis.end_date:
                    dis.active = False
                    dis.save()
        
        services = services.filter(serviceattribute__price__gte=min_price)
        services = services.filter(serviceattribute__price__lte=max_price)

        data = render_to_string('user_side/service_list.html', {"services": services,'discount_offer':discount_offer, "discounted_offer":discounted_offer})
       
        return JsonResponse({"data": data})
    except Exception as e:
        return JsonResponse({"error": str(e)})