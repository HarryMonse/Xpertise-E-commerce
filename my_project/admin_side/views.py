from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.contrib.auth import authenticate, login,logout
from user_side.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from user_side.forms import *
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import inlineformset_factory
from payment.models import *
from .forms import OrderForm




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




def admin_index(request):
    
    return render(request, 'admin_side/admin_index.html')




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

        allowed_payment_methods = ['COD']

        if order.payment.payment_method in allowed_payment_methods:
        #     with transaction.atomic():
        #         user_wallet = order.user.wallet if hasattr(order.user, 'wallet') else None

        #         if order.payment.payment_method == 'Razorpay':
        #             if user_wallet:
        #                 user_wallet.balance += order.order_total
        #                 user_wallet.save()

        #                 WalletHistory.objects.create(
        #                     wallet=user_wallet,
        #                     type='Credited',
        #                     amount=order.order_total,
        #                     created_at=timezone.now(),
        #                     reason='Admin Cancellation'
        #                 )
        #         elif order.payment.payment_method == 'Wallet':
        #             if user_wallet:
        #                 user_wallet.balance += order.order_total
        #                 user_wallet.save()

        #                 WalletHistory.objects.create(
        #                     wallet=user_wallet,
        #                     type='Credited',
        #                     amount=order.order_total,
        #                     created_at=timezone.now(),
        #                     reason='Admin Cancellation'
        #                 )

            for service_item in order.serviceorder_set.all():
                service_attribute = service_item.variations
                service_attribute.availability += service_item.quantity
                service_attribute.save()

        messages.success(request, f"Order with ID {order_number} has been cancelled successfully.")

    return redirect('order')