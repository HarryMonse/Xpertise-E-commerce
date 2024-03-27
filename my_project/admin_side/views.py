from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.contrib.auth import authenticate, login,logout
from user_side.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from user_side.forms import *
from django.db import IntegrityError
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.functions import TruncDate,TruncMonth, TruncYear
from django.db.models import Count
from django.forms.models import inlineformset_factory
from django.utils.timezone import make_aware
from django.views.decorators.cache import cache_control, never_cache
from datetime import datetime, timedelta
from payment.models import *
from .models import *
from .forms import *




# Create your views here.

def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user=authenticate(request, email=email,password=password)
        if user is not None and user.is_active and user.is_superadmin and user.is_staff and user.is_admin :
            login(request, user)
            messages.success(request, 'Successfully logged in.')
            return redirect('admin_index')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'admin_side/admin_login.html')
    return render(request, 'admin_side/admin_login.html')



def admin_logout(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect(admin_login)




@never_cache
@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_index(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
 
    service_count=Service.objects.count()
    category_count=category.objects.count()
    orders=CartOrder.objects.all()
    last_orders= CartOrder.objects.order_by('-created_at')[:5]
    orders_count=orders.count()
    total_users_count = CustomUser.objects.count()
    total = 0
    for order in orders:
        if order.status == 'Delivered':
            total += order.order_total
            
        if (order.payment and order.payment.payment_method == 'Razorpay' and order.status != 'Cancelled' ) or (order.payment and order.payment.payment_method == 'Wallet' and order.status != 'Cancelled'):
            total += order.order_total
    revenue=int(total)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    print('Start Date:', start_date)
    print('End Date:', end_date)

    daily_order_counts = (
            CartOrder.objects
            .filter(created_at__range=(start_date, end_date))
            .values('created_at')
            .annotate(order_count=Count('id'))
            .order_by('created_at')
        )
    print(f'daily orrderr {daily_order_counts}')
    print('SQL Query:', daily_order_counts.query)
    dates = [entry['created_at'].strftime('%Y-%m-%d') for entry in daily_order_counts]
    counts = [entry['order_count'] for entry in daily_order_counts]
    print('Daily Chart Data:')
    print('Dates:', [entry['created_at'] for entry in daily_order_counts])
    print('Counts:', [entry['order_count'] for entry in daily_order_counts])
    print(dates)
    print(counts)


    end_date = timezone.now()
    start_date = end_date - timedelta(days=365) 
    
    monthly_order_counts = (
        CartOrder.objects
        .filter(created_at__range=(start_date, end_date))   
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(order_count=Count('id'))
        .order_by('month')
    )
    monthlyDates = [entry['month'].strftime('%Y-%m') for entry in monthly_order_counts]
    monthlyCounts = [entry['order_count'] for entry in monthly_order_counts]
    
    yearly_order_counts = (
        CartOrder.objects
        .annotate(year=TruncYear('created_at'))
        .values('year')
        .annotate(order_count=Count('id'))
        .order_by('year')
    )
    yearlyDates = [entry['year'].strftime('%Y') for entry in yearly_order_counts]
    yearlyCounts = [entry['order_count'] for entry in yearly_order_counts]

    statuses = ['Delivered','Paid','Pending', 'New', 'Conformed', 'Cancelled', 'Return','Shipped']
    order_counts = [CartOrder.objects.filter(status=status).count() for status in statuses]

    context={
        'service_count':service_count,
        'category_count':category_count,
        'orders_count':orders_count,
        'dates': dates,
        'counts': counts,
        'monthlyDates':monthlyDates,
        'monthlyCounts':monthlyCounts,
        'yearlyDates':yearlyDates,
        'yearlyCounts':yearlyCounts,
        'last_orders': last_orders,
        'revenue':revenue,
        'total_users_count': total_users_count,
        'statuses': statuses,
        'order_counts': order_counts,
    }
    return render(request, 'admin_side/admin_index.html', context)




@login_required(login_url='admin_login')
def admin_service(request):
    item = Service.objects.filter(is_deleted=False)
    context = {
        "item":item
    }
    return render(request,'admin_side/service.html',context)




@login_required(login_url='admin_login')
def admin_service_add(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST,request.FILES)
        if form.is_valid():
            service=form.save(commit=False)
            service.save()
            images=request.FILES.getlist('images')
            for img in images:
                ServiceImages.objects.create(service=service,images=img)
            return redirect('admin_service')
    else:
        form = ServiceForm()    

    types = Type.objects.all()
    categories = category.objects.all()

    context = {
        'types': types,
        'categories': categories,
        'form' : form,
    }
    return render(request,'admin_side/service_add.html',context)


@login_required(login_url='admin_login')
def admin_service_edit(request, id):
    service = get_object_or_404(Service, id=id)
    types = Type.objects.all()
    categories = category.objects.all()

    ImageFormSet = inlineformset_factory(Service, ServiceImages, form=ServiceImagesForm, extra=1, can_delete=True)

    if request.method == 'POST':
        service_form = ServiceForm(request.POST, instance=service)
        formset = ImageFormSet(request.POST, request.FILES, instance=service)

        if service_form.is_valid() and formset.is_valid():
            service_form.save()
            formset.save()

            for form in formset.deleted_forms:
                instance = form.instance
                if instance.id:
                    instance.delete()

            return redirect('admin_service')

    else:
        service_form = ServiceForm(instance=service)
        formset = ImageFormSet(instance=service)

    context = {
        'service': service,
        'types': types,
        'categories': categories,
        'service_form': service_form,
        'formset': formset,
    }

    return render(request, 'admin_side/service_edit.html', context)

def admin_service_delete(request, id):
    service = get_object_or_404(Service, id=id)

    if request.method == 'POST':
        service.delete()
        return redirect('admin_service')

    context = {'service': service}
    return render(request, 'admin_side/service_delete.html', context)





@login_required(login_url='admin_login')
def customers(request):
    user = CustomUser.objects.all()
    context = {
        'user':user
    }
    return render(request, 'admin_side/customers.html',context)


@login_required(login_url='admin_login')
def block_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if not user.is_admin:
        user.is_active = not user.is_active
        user.save()

        messages.success(request, f'{user.username} has been {"blocked" if not user.is_active else "unblocked"}.')
    else:
        messages.warning(request, 'You cannot block/unblock the Superadmin.')

    return redirect('customers')



@login_required(login_url='admin_login')
def admin_category(request):
    data=category.objects.filter(is_deleted=False)
    context={
        'data':data
    }
    return render(request, 'admin_side/category.html', context)


@login_required(login_url='admin_login')
def admin_category_insert(request):
    if request.method == 'POST':
        category_name = request.POST.get('name')

        try:
            new_cat = category(category_name=category_name)
            new_cat.save()
            return redirect('admin_category')

        except IntegrityError as e:
            messages.error(request, f"Category '{category_name}' already exists.")
            return redirect('admin_category')

    return render(request, 'admin_side/category.html')



@login_required(login_url='admin_login')
def admin_category_edit(request,id):
    if request.method == 'POST':
        category_name = request.POST.get('name')
        edit=category.objects.get(id=id)
        edit.category_name = category_name
        edit.save()
        return redirect('admin_category')
    obj = category.objects.get(id=id)
    context = {
        "obj":obj
    }
    return render(request,'admin_side/category_edit.html', context)

@login_required(login_url='admin_login')
def admin_delete_category(request, id):
    category_to_delete = get_object_or_404(category, id=id)
    category_to_delete.is_deleted = True
    category_to_delete.save()
    return redirect('admin_category')

@login_required(login_url='admin_login')
def block_unblock_category(request, id):
    category_to_block = get_object_or_404(category, id=id)
    category_to_block.is_blocked = not category_to_block.is_blocked
    category_to_block.save()
    return redirect('admin_category')



@login_required(login_url='admin_login')
def admin_type(request):
    data=Type.objects.all()
    context={
        'data':data
    }
    return render(request, 'admin_side/type.html', context)


@login_required(login_url='admin_login')
def admin_type_insert(request):
    if request.method == 'POST':
        type_name = request.POST.get('name')
        try:
            new_type = Type(type_name=type_name)
            new_type.save()
            messages.success(request, f"Type '{type_name}' added successfully.")
        except IntegrityError:
            messages.error(request, f"Type '{type_name}' already exists.")
        return redirect('admin_type')
    
    return render(request, 'admin_side/type.html')

@login_required(login_url='admin_login')
def admin_type_edit(request,id):
    if request.method == 'POST':
        type_name = request.POST.get('name')
        edit=Type.objects.get(id=id)
        edit.type_name = type_name
        edit.save()
        return redirect('admin_type')
    obj = Type.objects.get(id=id)
    context = {
        "obj":obj
    }
    return render(request,'admin_side/type_edit.html', context)


@login_required(login_url='admin_login')
def type_available(request, type_id):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    type = get_object_or_404(Type, id=type_id)
    
    if type.is_active:
        type.is_active=False
       
    else:
        type.is_active=True
    type.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin_login')
def admin_varient(request):
    cat=category.objects.all()
    item = ServiceAttribute.objects.filter(is_deleted=False)
    context = {
        "item":item,
        "cat":cat
    }
    return render(request,'admin_side/varient.html', context)


@login_required(login_url='admin_login')
def admin_varient_add(request):
    if request.method == 'POST':
        form = ServiceAttributeForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.save()
            return redirect('admin_varient')
    else:
        form = ServiceAttributeForm()    

    types = Type.objects.all()
    categories = category.objects.all()

    context = {
        'types': types,
        'categories': categories,
        'form' : form,
    }
    return render(request, 'admin_side/varient_add.html', context)


@login_required(login_url='admin_login')
def admin_varient_edit(request, id):
    service = get_object_or_404(ServiceAttribute, id=id)

    if request.method == 'POST':
        service_form = ServiceAttributeForm(request.POST, request.FILES, instance=service)
        if service_form.is_valid():
            service_form.save()
            return redirect('admin_varient')

    else:
        service_form = ServiceAttributeForm(instance=service)

    context = {
        'service_form': service_form,
        'service': service,
    }

    return render(request, 'admin_side/varient_edit.html', context)


def admin_varient_delete(request, id):
    service = get_object_or_404(ServiceAttribute, id=id)

    if request.method == 'POST':
        service.delete()
        return redirect('admin_varient')

    context = {'service': service}
    return render(request, 'admin_side/service_delete.html', context)





@login_required(login_url='admin_login')
def admin_provider_type(request):
    data=ProviderType.objects.all()
    context={
        'data':data
    }
    return render(request, 'admin_side/provider_type.html', context)

@login_required(login_url='admin_login')
def admin_provider_type_insert(request):
    if request.method == 'POST':
        provider_type_name = request.POST.get('name').strip()  
        provider_type_code = request.POST.get('code').strip()  
        
        try:
    
            existing_provider_type = ProviderType.objects.filter(provider_type_name__iexact=provider_type_name).first()
            if existing_provider_type:
                messages.error(request, f"Provider type '{provider_type_name}' already exists.")
            else:
                new_provider_type = ProviderType(provider_type_name=provider_type_name, provider_type_code=provider_type_code)
                new_provider_type.save()
                messages.success(request, f"Provider type '{provider_type_name}' added successfully.")
        except IntegrityError:
            messages.error(request, f"An error occurred while adding the provider type.")

        return redirect('admin_provider_type')

    return render(request, 'admin_side/provider_type.html')

@login_required(login_url='admin_login')
def admin_provider_type_edit(request,id):
    if request.method == 'POST':
        provider_type_name = request.POST.get('name')
        provider_type_code = request.POST.get('code')
        edit=ProviderType.objects.get(id=id)
        edit.provider_type_name = provider_type_name
        edit.provider_type_code = provider_type_code
        edit.save()
        return redirect('admin_provider_type')
    obj = ProviderType.objects.get(id=id)
    context = {
        "obj":obj
    }
    return render(request,'admin_side/provider_type_edit.html', context)



@login_required(login_url='admin_login')
def order(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    status='all'
    order = CartOrder.objects.order_by('-created_at')
    form = OrderForm(request.POST or None)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            if status != 'all':
                order = order.filter(status=status)

    context = {
        'order':order,
        'form':form,
        'status':status
    }
    return render(request, 'admin_side/order.html',context)


@login_required(login_url='admin_login')
def orderitems(request, order_number):
    if not request.user.is_superadmin:
        return redirect('admin_login')

    try:
        order = CartOrder.objects.get(id=order_number)
    except Exception as e:
        print(e)

    order_items = ServiceOrder.objects.filter(order=order)
    address = order.selected_address
    payment = Payments.objects.all()

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            if form.cleaned_data['status'] == 'Cancelled':
                cancell_order(request, order_number)
                return redirect('order')
            else:
                form.save()
                return redirect('orderitems', order_number=order.pk)
        else:
            messages.error(request, "Choose a valid status")
            return redirect('orderitems', order_number=order.pk)

    form = OrderForm(instance=order)

    context = {
        'order': order,
        'address': address,
        'order_items': order_items,
        'form': form,
        'payment': payment
    }
    return render(request, 'admin_side/order_items.html', context)


@login_required(login_url='admin_login')
def cancell_order(request, order_number):
    if not request.user.is_superadmin:
        return redirect('admin_login')

    try:
        order = CartOrder.objects.get(id=order_number)
    except CartOrder.DoesNotExist:
        messages.error(request, f"Order with ID {order_number} does not exist.")
        return redirect('order')

    if order.status == 'Cancelled':
        messages.warning(request, f"Order with ID {order_number} is already cancelled.")
    else:
        order.status = 'Cancelled'
        order.save()

        allowed_payment_methods = ['Razorpay', 'Wallet']

        if order.payment.payment_method in allowed_payment_methods:
            with transaction.atomic():
                user_wallet = order.user.wallet if hasattr(order.user, 'wallet') else None

                if order.payment.payment_method == 'Razorpay':
                    if user_wallet:
                        user_wallet.balance += order.order_total
                        user_wallet.save()

                        WalletHistory.objects.create(
                            wallet=user_wallet,
                            type='Credited',
                            amount=order.order_total,
                            created_at=timezone.now(),
                            reason='Admin Cancellation'
                        )
                elif order.payment.payment_method == 'Wallet':
                    if user_wallet:
                        user_wallet.balance += order.order_total
                        user_wallet.save()

                        WalletHistory.objects.create(
                            wallet=user_wallet,
                            type='Credited',
                            amount=order.order_total,
                            created_at=timezone.now(),
                            reason='Admin Cancellation'
                        )

            for service_item in order.serviceorder_set.all():
                service_attribute = service_item.variations
                service_attribute.availability += service_item.quantity
                service_attribute.save()

        messages.success(request, f"Order with ID {order_number} has been cancelled successfully.")

    return redirect('order')


@login_required(login_url='admin_login')
def service_offers(request):
    offers=ServiceOffer.objects.all()
    try:
        service_offer = ServiceOffer.objects.get(active=True)
        print(service_offer)
    except ServiceOffer.DoesNotExist:
        service_offer = None
    services = ServiceAttribute.objects.all()
    for p in services:
        if service_offer:
            discounted_price = p.old_price - (p.old_price * service_offer.discount_percentage / 100)
            p.price = max(discounted_price, Decimal('0.00'))  
        else:          
            p.price = p.old_price
        p.save()
    context={
        'offers':offers
    }
    return render(request, 'admin_side/service_offers.html',context)

@login_required(login_url='admin_login')
def create_service_offer(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    if request.method == 'POST':
        form = ServiceOfferForm(request.POST)
        if form.is_valid():
            discount_percentage = form.cleaned_data['discount_percentage']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            active = form.cleaned_data['active']
            
            if end_date and start_date and end_date < start_date:
                messages.error(request, 'Expiry date must not be less than the start date.')
            else:
                current_date = timezone.now()
                if start_date and end_date and (current_date < start_date or current_date > end_date):
                    active = False
                    messages.error(request, 'Offer cannot be activated now. Check the start date.')

                if active:
                    ServiceOffer.objects.update(active=False)

                if discount_percentage or start_date or end_date or active:
                    form.save()
            
            return redirect('service-offers')  
    else:
        form = ServiceOfferForm()

    return render(request, 'admin_side/create-service-offers.html', {'form': form})


@login_required(login_url='admin_login')
def edit_service_offers(request, id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    offer_discount = get_object_or_404(ServiceOffer, id=id)
    print(f'Active Date: {offer_discount.start_date}')

    if request.method == 'POST':
        discount = request.POST['discount']
        active = request.POST.get('active') == 'on'
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        
        if end_date and start_date and end_date < start_date:
            messages.error(request, 'Expiry date must not be less than the start date.')
        else:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            current_date = timezone.now()
            if start_date and end_date and (current_date < start_date or current_date > end_date):
                active = False
                messages.error(request, 'Offer cannot be activated now. Check the start date.')
           
            active_category_offer = CategoryOffer.objects.filter(active=True).first()

            if active_category_offer:
               
                messages.error(request, 'Cannot create/update service offer when a category offer is active.')
                return redirect('service-offers')

            if active:
                ServiceOffer.objects.exclude(id=offer_discount.id).update(active=False)

            offer_discount.discount_percentage = discount or None
            offer_discount.start_date = start_date or None
            offer_discount.end_date = end_date or None
            offer_discount.active = active
            offer_discount.save()

            messages.success(request, 'Offer Updated successfully')
            return redirect('service-offers')
    
    return render(request, 'admin_side/edit_service_offers.html', {'offer_discount': offer_discount})


@login_required(login_url='admin_login')
def delete_service_offer(request,id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    try:
        offer= get_object_or_404(ServiceOffer, id=id)
    except ValueError:
        return redirect('service-offers')
    offer.delete()
    messages.warning(request,"Offer has been deleted successfully")
    return redirect('service-offers')

@login_required(login_url='admin_login')
def category_offers(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    offers = CategoryOffer.objects.all()
    categories = category.objects.all()

    for cate in categories:
        try:
            category_offer = CategoryOffer.objects.filter(category=cate, active=True)
            print(category_offer)
        except CategoryOffer.DoesNotExist:
            category_offer = None
        services = ServiceAttribute.objects.filter(service__category=cate, is_available=True)
        print(services)
        
        for service in services:
            if category_offer:
                for cat in category_offer:
                    discounted_price = service.old_price - (service.old_price * cat.discount_percentage / 100)
                    service.price = max(discounted_price, Decimal('0.00'))  
            else:
                service.price=service.old_price
            service.save()
    context = {
        'offers': offers
    }
    return render(request, 'admin_side/category_offers.html', context)


@login_required(login_url='admin_login')
def create_category_offer(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            discount_percentage = form.cleaned_data['discount_percentage']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            active = form.cleaned_data['active']

            if end_date and start_date and end_date < start_date:
                messages.error(request, 'Expiry date must not be less than the start date.')
            else:
               
                if active and CategoryOffer.objects.filter(category=category, active=True).exists():
                    messages.error(request, 'An active offer already exists for this category.')
                   
                else:
                    current_date = timezone.now()
                    if start_date and end_date and (current_date < start_date or current_date > end_date):
                        active = False
                        messages.error(request, 'Offer cannot be activated now. Check on start date')   
                    if active:
                        CategoryOffer.objects.update(active=False)
                    if discount_percentage or start_date or end_date or active:
                        form.save()
                    return redirect('category-offers')  
    else:
        form = CategoryOfferForm()
    return render(request, 'admin_side/create_category_offer.html', {'form': form})


@login_required(login_url='admin_login')
def edit_category_offers(request, id):
    if not request.user.is_superadmin:
        return redirect('admin_login')

    offer_discount = get_object_or_404(CategoryOffer, id=id)
    print(f'Active Date: {offer_discount.start_date}')

    if request.method == 'POST':
        discount = request.POST.get('discount')
        active = request.POST.get('active') == 'on'
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if end_date and start_date:
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))

            if end_date < start_date:
                messages.error(request, 'Expiry date must not be less than the start date.')
                return redirect('edit-category-offers', id=id)
   
            current_date = timezone.now()
            if start_date and end_date and (current_date < start_date or current_date > end_date):
                active = False
                messages.error(request, 'Offer cannot be activated now. Check the start date.')

        active_service_offer = ServiceOffer.objects.filter(active=True).first()

        if active_service_offer:
            
            messages.error(request, 'Cannot activate category offer when a service offer is active.')
            return redirect('category-offers')
        
        if active:
            CategoryOffer.objects.exclude(id=offer_discount.id).update(active=False)

        offer_discount.discount_percentage = discount or None
        offer_discount.start_date = start_date or None
        offer_discount.end_date = end_date or None
        offer_discount.active = active
        offer_discount.save()

        messages.success(request, 'Offer updated successfully')
        return redirect('category-offers')
    return render(request,'admin_side/edit_category_offers.html', {'offer_discount': offer_discount})

@login_required(login_url='admin_login')
def delete_category_offer(request,id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    try:
        offer= get_object_or_404(CategoryOffer, id=id)
    except ValueError:
        return redirect('category-offers')
    offer.delete()
    messages.warning(request,"Offer has been deleted successfully")

    return redirect('category-offers')



@login_required(login_url='admin_login')
def admin_coupon(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    coupon = Coupon.objects.all()
    return render(request, 'admin_side/admin_coupon.html',{'coupon':coupon})

@login_required(login_url='admin_login')
def create_coupon(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    if request.method == 'POST':
        code = request.POST['code']
        discount = request.POST['discount']
        active = request.POST.get('active') == 'on'
        active_date = request.POST['active_date']
        expiry_date = request.POST['expiry_date']

        if active_date > expiry_date:
            messages.error(request, 'Active date should not be greater than expiry date')
            return render(request, 'admin_side/create_coupon.html')

        if Coupon.objects.filter(code=code).exists():
            messages.error(request, f'Coupon with code {code} already exists')
            return render(request, 'admin_side/create_coupon.html')

        coupon = Coupon(
            code=code,
            discount=discount,
            active=active,
            active_date=active_date,
            expiry_date=expiry_date
        )
        coupon.save()
        messages.success(request, 'Coupon created successfully')
        return redirect('admin_coupon')

    return render(request, 'admin_side/create_coupon.html')

@login_required(login_url='admin_login')
def edit_coupon(request,id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    coupon_code = get_object_or_404(Coupon, id=id)
    print(f'Active Date: {coupon_code.active_date}')
    if request.method == 'POST':
        code = request.POST['code']
        discount = request.POST['discount']
        active = request.POST.get('active') == 'on'
        active_date = request.POST['active_date']
        expiry_date = request.POST['expiry_date']
        
        if active_date > expiry_date:
            messages.error(request, 'Active date should not be greater than expiry date')
            return render(request, 'admin_side/create_coupon.html')
        
        coupon_code.code=code
        coupon_code.discount=discount
        coupon_code.active_date=active_date
        coupon_code.expiry_date=expiry_date
        coupon_code.active=active
        coupon_code.save()
        messages.success(request, 'Coupon Updated successfully')
        return redirect('admin_coupon')
    return render (request, 'admin_side/update_coupon.html',{'coupon_code':coupon_code})

@login_required(login_url='admin_login')        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_coupon(request,id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    try:
        coupon= get_object_or_404(Coupon, id=id)
    except ValueError:
        return redirect('admin_coupon')
    coupon.delete()
    messages.warning(request,"Coupon has been deleted successfully")

    return redirect('admin_coupon')  


@login_required(login_url='admin_login')
def sales_report(request):
    if not request.user.is_superadmin:
        return redirect(admin_login)
    start_date_value = ""
    end_date_value = ""
    try:
        orders=CartOrder.objects.filter(is_ordered= True).order_by('-created_at')
    except:
        pass
    if request.method == 'POST':
       
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date_value = start_date
        end_date_value = end_date
        if start_date and end_date:
          
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

           
            orders = orders.filter(created_at__range=(start_date, end_date))
   
    context={
        'orders':orders,
        'start_date_value':start_date_value,
        'end_date_value':end_date_value
    }

    return render(request,'admin_side/sales_report.html',context)


@login_required(login_url='admin_login')
def admin_banner(request):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    today = timezone.now().date()
    banners = Banner.objects.all()
    for banner in banners:
        banner.is_active=banner.update_status()
        banner.save()

    return render(request, 'admin_side/admin_banner.html',{'banners':banners})

@login_required(login_url='admin_login')
def create_banner(request):
    if not request.user.is_superadmin:
        redirect('admin_login')
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid:
            form.save()
            return redirect('admin_banner')
    else:
        form = BannerForm()

    return render(request,'admin_side/banner_create.html',{'form':form})


@login_required(login_url='admin_login')
def update_banner(request, id):
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    banner = get_object_or_404(Banner,id=id)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES , instance=banner)
        if form.is_valid:
            form.save()
            return redirect('admin_banner')
    else:
        form = BannerForm(instance=banner)
    context={
        'form':form,
        'banner':banner
    }
    return render(request, 'admin_side/banner_update.html',context)

@login_required(login_url='admin_login')
def delete_banner(request, id):
    if not request.user.is_superadmin:
        redirect('admin_login')
    
    try:
        banner = get_object_or_404(Banner,id=id)
    except ValueError:
        return redirect('admin_banner')
    banner.delete()
    messages.warning(request,"Banner deleted successfully")
    return redirect('admin_banner')