from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import AddressForm

from .models import *







# Create your views here.


@never_cache
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def checkout(request):
    user=request.user 
    items=CartItem.objects.filter(user=user, is_deleted=False)
    user_addresses = Address.objects.filter(users=request.user)
    
    address_form = AddressForm(request.POST or None)
    totals = request.session.get('totals', 0)
    total = request.session.get('total', 0)
    discounts = request.session.get('discounts', 0)

    # wallet = Wallet.objects.filter(user=user).first()
    # wallet_balance = wallet.balance if wallet else 0
    # print('Wallet balance:', wallet_balance)

    # wallet_button_disabled = total > wallet_balance
    print(total)
    print(totals)
    print(discounts)

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


            return render(request, 'paymenthome/payment.html', {
               
                'selected_address': selected_address,
                'items':items,
                'total':total,
                'totals':totals,
                'discounts': discounts,
                # 'wallet_balance': wallet_balance,
                # 'wallet_button_disabled': wallet_button_disabled,
            })
        
        elif address_form.is_valid():
            address_instance = address_form.save(commit=False)
            address_instance.users = request.user
            address_instance.save()
            CartItem.objects.filter(user=user, is_deleted=False).update(address=address_instance)
            return render(request, 'paymenthome/payment.html', {
             
                'new_address': address_instance,
                'items':items,
                'total':total,
                'totals':totals,
                'discounts': discounts,
                # 'wallet_balance': wallet_balance,
                # 'wallet_button_disabled': wallet_button_disabled,
            })
    

    return render(request, 'payment/checkout.html',{'user_addresses': user_addresses,'items':items,'total':total,'totals':totals,'discounts': discounts})


@never_cache
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
    
        # currency = 'INR'
        # amount_in_paise = amount  * 100
 
        # razorpay_order = razorpay_client.order.create(dict(amount=amount_in_paise,
        #                                                    currency=currency,
        #                                                    payment_capture='0'))
 
        # razorpay_order_id = razorpay_order['id']
        # callback_url = 'paymenthandler/'
 
        context = {
            'total': total,
            'items': items,
            'totals': totals,
            'discounts': discounts,
            'user_addresses': user_addresses,
        }
        # context['razorpay_order_id'] = razorpay_order_id
        # context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
        # context['razorpay_amount'] = amount_in_paise
        # context['currency'] = currency
        # context['callback_url'] = callback_url
 
        return render(request, 'payment/payment.html', context=context)