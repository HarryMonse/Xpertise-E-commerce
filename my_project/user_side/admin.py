from django.contrib import admin
from .models import *

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class CategoryAdmin(admin.ModelAdmin):
    list_display=['category_name']
class TypeAdmin(admin.ModelAdmin):
    list_display=['type_name']
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display=['product_name','category','is_available']
class ColorAdmin(admin.ModelAdmin):
    list_display=['provider_type_name','provider_type_code']
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display=['id','product','price','old_price','provider_type','stock','image_tag']


# Register your models here.

admin.site.register(CustomUser  )
admin.site.register(category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Type,TypeAdmin)
admin.site.register(ProviderType)
admin.site.register(ProductAttribute,ProductAttributeAdmin)

