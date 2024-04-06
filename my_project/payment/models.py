from django.db import models
from user_side.models import *
from admin_side.models import *

# Create your models here.


class Address(models.Model):
    users = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=200)
    district = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceAttribute, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total=models.BigIntegerField(null=True)
    timestamp = models.DateTimeField(default=timezone.now,null=True)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    coupon=models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.service.service.service_name}"
    def get_subtotal(self):
        return self.service.price * self.quantity
    
    def get_total_price(self):
        if self.items.exists():
            return sum(item.get_subtotal() for item in self.items.all())
        else:
            return 0
        


class Wallet(models.Model):
    user=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance=models.IntegerField(default=0)
    
class WalletHistory(models.Model):
    wallet=models.ForeignKey(Wallet, on_delete=models.CASCADE)
    type=models.CharField(null=True, blank=True, max_length=20)
    created_at=models.DateField(auto_now_add=True)
    amount=models.IntegerField()
    reason = models.CharField(max_length=255,blank=True,null=True)

        

class Payments(models.Model):
    payment_choices=(
        ('COD','COD'),
        ('Razorpay','Razorpay'),
        ('Wallet','Wallet'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100,choices=payment_choices)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name
    
class CartOrder(models.Model):
    STATUS =(
        ('New','New'),
        ('Paid','Paid'),
        ('Processed','Processed'),
        ('Confirmed','Confirmed'),
        ('Pending','Pending'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled'),
        ('Refund','Refund')
    )
    user=models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payments,on_delete=models.SET_NULL,blank=True,null=True)
    order_number = models.CharField(max_length=20,default=None)
    order_total = models.FloatField(null=True, blank=True)
    status=models.CharField(max_length=10, choices=STATUS, default='New')
    ip =  models.CharField(blank=True,max_length=20)
    is_ordered=models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=True)
    updated_at=models.DateTimeField(auto_now=True)
    selected_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    coupon=models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Cart Order"
    
    def __str__(self):
        return self.order_number

class ServiceOrder(models.Model):
    order=models.ForeignKey(CartOrder,on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payments,on_delete=models.SET_NULL,blank=True,null=True)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    service=models.ForeignKey(Service,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    service_price=models.FloatField(default=0)
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    variations =  models.ForeignKey(ServiceAttribute, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.service.service_name
