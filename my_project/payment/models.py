from django.db import models
from user_side.models import *

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
    # coupon=models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
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
