from django.contrib import admin
from .models import *

class ServiceImagesAdmin(admin.TabularInline):
    model = ServiceImages

class CategoryAdmin(admin.ModelAdmin):
    list_display=['category_name']
class TypeAdmin(admin.ModelAdmin):
    list_display=['type_name']
class ServiceAdmin(admin.ModelAdmin):
    inlines = [ServiceImagesAdmin]
    list_display=['service_name','category','is_available']
class ColorAdmin(admin.ModelAdmin):
    list_display=['provider_type_name','provider_type_code']
class ServiceAttributeAdmin(admin.ModelAdmin):
    list_display=['id','service','price','old_price','provider_type','stock','image_tag']


# Register your models here.

admin.site.register(CustomUser  )
admin.site.register(category,CategoryAdmin)
admin.site.register(Service,ServiceAdmin)
admin.site.register(Type,TypeAdmin)
admin.site.register(ProviderType)
admin.site.register(ServiceAttribute,ServiceAttributeAdmin)

