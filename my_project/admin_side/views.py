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
def admin_service_edit(request, id):
    product = get_object_or_404(Product, id=id)
    brands = Brand.objects.all()
    categories = category.objects.all()

    ImageFormSet = inlineformset_factory(Product, ProductImages, form=ProductImagesForm, extra=1, can_delete=True)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, instance=product)
        formset = ImageFormSet(request.POST, request.FILES, instance=product)

        if product_form.is_valid() and formset.is_valid():
            product_form.save()
            formset.save()

            for form in formset.deleted_forms:
                instance = form.instance
                if instance.id:
                    instance.delete()

            return redirect('admin_service')

    else:
        product_form = ProductForm(instance=product)
        formset = ImageFormSet(instance=product)

    context = {
        'product': product,
        'brands': brands,
        'categories': categories,
        'product_form': product_form,
        'formset': formset,
    }

    return render(request, 'admin_side/service_edit.html', context)

def admin_service_delete(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.delete()
        return redirect('admin_service')

    context = {'product': product}
    return render(request, 'admin_side/service_delete.html', context)





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

@login_required(login_url='admin_login')
def admin_type_edit(request,id):
    if request.method == 'POST':
        brand_name = request.POST.get('name')
        edit=Brand.objects.get(id=id)
        edit.brand_name = brand_name
        edit.save()
        return redirect('admin_type')
    obj = Brand.objects.get(id=id)
    context = {
        "obj":obj
    }
    return render(request,'admin_side/type_edit.html', context)


@login_required(login_url='admin_login')
def type_available(request, brand_id):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    if not request.user.is_superadmin:
        return redirect('admin_login')
    
    brand = get_object_or_404(Brand, id=brand_id)
    
    if brand.is_active:
        brand.is_active=False
       
    else:
        brand.is_active=True
    brand.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin_login')
def admin_varient(request):
    cat=category.objects.all()
    item = ProductAttribute.objects.filter(is_deleted=False)
    context = {
        "item":item,
        "cat":cat
    }
    return render(request,'admin_side/varient.html', context)


@login_required(login_url='admin_login')
def admin_varient_add(request):
    if request.method == 'POST':
        form = ProductAttributeForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect('admin_varient')
    else:
        form = ProductAttributeForm()    

    brands = Brand.objects.all()
    categories = category.objects.all()

    context = {
        'brands': brands,
        'categories': categories,
        'form' : form,
    }
    return render(request, 'admin_side/varient_add.html', context)


@login_required(login_url='admin_login')
def admin_varient_edit(request, id):
    product = get_object_or_404(ProductAttribute, id=id)

    if request.method == 'POST':
        product_form = ProductAttributeForm(request.POST, request.FILES, instance=product)
        if product_form.is_valid():
            product_form.save()
            return redirect('admin_varient')

    else:
        product_form = ProductAttributeForm(instance=product)

    context = {
        'product_form': product_form,
        'product': product,
    }

    return render(request, 'admin_side/varient_edit.html', context)


def admin_varient_delete(request, id):
    product = get_object_or_404(ProductAttribute, id=id)

    if request.method == 'POST':
        product.delete()
        return redirect('admin_varient')

    context = {'product': product}
    return render(request, 'admin_side/service_delete.html', context)





@login_required(login_url='admin_login')
def admin_provider_type(request):
    data=Color.objects.all()
    context={
        'data':data
    }
    return render(request, 'admin_side/provider_type.html', context)

@login_required(login_url='admin_login')
def admin_provider_type_insert(request):
    if request.method == 'POST':
        color_name = request.POST.get('name').strip()  
        color_code = request.POST.get('code').strip()  
        
        try:
    
            existing_color = Color.objects.filter(color_name__iexact=color_name).first()
            if existing_color:
                messages.error(request, f"Provider type '{color_name}' already exists.")
            else:
                new_color = Color(color_name=color_name, color_code=color_code)
                new_color.save()
                messages.success(request, f"Provider type '{color_name}' added successfully.")
        except IntegrityError:
            messages.error(request, f"An error occurred while adding the provider type.")

        return redirect('admin_provider_type')

    return render(request, 'admin_side/provider_type.html')

@login_required(login_url='admin_login')
def admin_provider_type_edit(request,id):
    if request.method == 'POST':
        color_name = request.POST.get('name')
        color_code = request.POST.get('code')
        edit=Color.objects.get(id=id)
        edit.color_name = color_name
        edit.color_code = color_code
        edit.save()
        return redirect('admin_provider_type')
    obj = Color.objects.get(id=id)
    context = {
        "obj":obj
    }
    return render(request,'admin_side/provider_type_edit.html', context)