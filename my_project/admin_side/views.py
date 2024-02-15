from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.contrib.auth import authenticate, login,logout
from user_side.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from user_side.forms import *
from django.db import IntegrityError








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
    item = Product.objects.filter(is_deleted=False)
    context = {
        "item":item
    }
    return render(request,'admin_side/service.html',context)




@login_required(login_url='admin_login')
def admin_service_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            product=form.save(commit=False)
            product.save()
            images=request.FILES.getlist('images')
            for img in images:
                ProductImages.objects.create(product=product,images=img)
            return redirect('admin_service')
    else:
        form = ProductForm()    

    brands = Brand.objects.all()
    categories = category.objects.all()

    context = {
        'brands': brands,
        'categories': categories,
        'form' : form,
    }
    return render(request,'admin_side/service_add.html',context)





@login_required(login_url='admin_login')
def customers(request):
    user = User.objects.all()
    context = {
        'user':user
    }
    return render(request, 'admin_side/customers.html',context)


@login_required(login_url='admin_login')
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

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
def admin_type(request):
    data=Brand.objects.all()
    context={
        'data':data
    }
    return render(request, 'admin_side/type.html', context)


@login_required(login_url='admin_login')
def admin_type_insert(request):
    if request.method == 'POST':
        brand_name = request.POST.get('name')
        try:
            new_brand = Brand(brand_name=brand_name)
            new_brand.save()
            messages.success(request, f"Brand '{brand_name}' added successfully.")
        except IntegrityError:
            messages.error(request, f"Brand '{brand_name}' already exists.")
        return redirect('admin_type')
    
    return render(request, 'admin_side/type.html')