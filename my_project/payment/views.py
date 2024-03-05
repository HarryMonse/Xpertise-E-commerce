import random
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from .forms import AddressForm
from datetime import datetime
from .models import *


# Create your views here.


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def checkout(request):
    user=request.user 
    items=CartItem.objects.filter(user=user, is_deleted=False)
    user_addresses = Address.objects.filter(users=request.user)
    
    address_form = AddressForm(request.POST or None)
    totals = request.session.get('totals', 0)
    total = request.session.get('total', 0)
    print(total)
    print(totals)
    
    if request.session.get('order_placed', False):
        del request.session['order_placed']
        return redirect('user_index')  


    if request.method == 'POST':
        print("entered")
        if 'use_existing_address' in request.POST:
            selected_address_id = request.POST.get('existing_address')
            selected_address = get_object_or_404(Address, id=selected_address_id)
            # Update the address for all CartItems in the user's cart
            CartItem.objects.filter(user=user, is_deleted=False).update(address=selected_address)


            return render(request, 'payment/payment.html', {
               
                'selected_address': selected_address,
                'items':items,
                'total':total,
                'totals':totals,
                

            })
        
        elif address_form.is_valid():
            address_instance = address_form.save(commit=False)
            address_instance.users = request.user
            address_instance.save()
            CartItem.objects.filter(user=user, is_deleted=False).update(address=address_instance)
            return render(request, 'payment/payment.html', {
             
                'new_address': address_instance,
                'items':items,
                'total':total,
                'totals':totals,
                

            })
    

    return render(request, 'payment/checkout.html',{'user_addresses': user_addresses,'items':items,'total':total,'totals':totals}) #,'discounts': discounts})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def payment(request):
    print("Entering payment")
    user=request.user 
    items=CartItem.objects.filter(user=user, is_deleted=False)
    user_addresses = Address.objects.filter(users=request.user)
    totals = request.session.get('totals', 0)
    total = request.session.get('total', 0)
    discounts = request.session.get('discounts', 0)

    if request.session.get('order_placed', False):
        del request.session['order_placed']
        return redirect('user_index')  


    if request.method == "POST":
        amount = request.POST.get('total', 0)
        amount = int(amount)
    
        


 
        context = {
            'total': total,
            'items': items,
            'totals': totals,
            'discounts': discounts,
            'user_addresses': user_addresses,
        }
        


 
        return render(request, 'payment/payment.html', context=context)
    


def place_order(request):
    user = request.user 
    items = CartItem.objects.filter(user=user, is_deleted=False)

    request.session.get('totals', 0)
    total = request.session.get('total', 0)
    request.session.get('discounts', 0)
   

     
    if items.exists():
        user_addresses = items.first().address
    else:
        user_addresses = None


    short_id = str(random.randint(1000, 9999))
    yr = datetime.now().year
    dt = int(datetime.today().strftime('%d'))
    mt = int(datetime.today().strftime('%m'))
    d = datetime(yr, mt, dt).date()
    payment_id = f"PAYMENT-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    current_date = d.strftime("%Y%m%d")
    short_id = str(random.randint(1000, 9999))
    order_numbers = current_date + short_id 
    



    var=CartOrder.objects.create(
        user=request.user,
        order_number=order_numbers,
        order_total= total,
        

        selected_address=user_addresses,
        ip=request.META.get('REMOTE_ADDR')    
    )
    var.save()
    payment_instance=Payments.objects.create(
        user=request.user,
        payment_id=payment_id,
        payment_method='COD',
        amount_paid= total,
        status='Pending',
                
    )
        
    var.payment=payment_instance
    var.save()
            
    cart=CartItem.objects.filter(user=request.user)
            
    for item in cart:
        orderedservice=ServiceOrder()
        item.service.availability-=item.quantity
        item.service.save()
        orderedservice.order=var
        orderedservice.payment=payment_instance
        orderedservice.user=request.user
        orderedservice.service=item.service.service
        orderedservice.quantity=item.quantity
        orderedservice.service_price=item.service.price
        service_attribute = ServiceAttribute.objects.get(service=item.service.service, provider_type=item.service.provider_type)
        orderedservice.variations = service_attribute
        orderedservice.ordered=True
        orderedservice.save()
        item.delete()  
   


        
    return redirect('order_success')




@cache_control(no_cache=True, must_revalidate=True, no_store=True)    
@login_required(login_url='user_login')
def order_success(request):
    order = CartOrder.objects.filter(user=request.user).order_by('-id').first()
    print(order) 
    service_orders = ServiceOrder.objects.filter(order=order)
    
    
    request.session['order_placed'] = True
    context = {
        'order':order,
        'order_number': order.order_number,
        'order_status': order.status,
        'service_orders': service_orders,
    }
    return render(request,'payment/orderdetail.html',context)