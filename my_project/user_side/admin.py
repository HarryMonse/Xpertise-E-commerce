from django.contrib import admin
from .models import*

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class CategoryAdmin(admin.ModelAdmin):
    list_display=['category_name']
class BrandAdmin(admin.ModelAdmin):
    list_display=['brand_name']
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display=['product_name','category','is_available']
class ColorAdmin(admin.ModelAdmin):
    list_display=['color_name','color_code']
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display=['id','product','price','old_price','color','stock','image_tag']


# Register your models here.

admin.site.register(User)
admin.site.register(category)
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Color)
admin.site.register(ProductAttribute,ProductAttributeAdmin)

