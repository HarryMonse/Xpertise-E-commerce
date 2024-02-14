from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.contrib.auth import authenticate, login,logout
from user_side.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404






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
    # item = Service.objects.filter(is_deleted=False)
    # context = {
    #     "item":item
    # }
    return render(request,'admin_side/service.html')




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