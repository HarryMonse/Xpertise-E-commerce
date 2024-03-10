from django.contrib import admin
from .models import *

class CouponAdmin(admin.ModelAdmin):
    list_display=['code','discount','active','active_date','expiry_date','created_date']


# Register your models here.


admin.site.register(ServiceOffer)
admin.site.register(CategoryOffer)
admin.site.register(Coupon,CouponAdmin)