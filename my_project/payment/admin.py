from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(Address)
admin.site.register(CartItem)
admin.site.register(Wallet)
admin.site.register(WalletHistory)
admin.site.register(Payments)
admin.site.register(CartOrder)
admin.site.register(ServiceOrder)
