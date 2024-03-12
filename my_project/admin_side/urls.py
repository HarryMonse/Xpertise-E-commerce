from django.urls import path
from admin_side import views


urlpatterns = [
    path('admin_login', views.admin_login , name ='admin_login'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('admin_index/',views.admin_index,name='admin_index'),
    path('admin_service/',views.admin_service,name='admin_service'),   
    path('admin_service_add/',views.admin_service_add,name='admin_service_add'),
    path('admin_service_edit/<int:id>',views.admin_service_edit,name='admin_service_edit'),
    path('admin_service_delete/<int:id>',views.admin_service_delete,name='admin_service_delete'),  
    path('customers/',views.customers,name='customers'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('admin_category/',views.admin_category,name='admin_category'),
    path('admin_category_insert/',views.admin_category_insert,name='admin_category_insert'),
    path('admin_type/',views.admin_type,name='admin_type'), 
    path('admin_type_insert/',views.admin_type_insert,name='admin_type_insert'),
    path('admin_type_edit/<int:id>',views.admin_type_edit,name='admin_type_edit'),
    path('type_available/<int:type_id>/',views.type_available,name='type_available'),
    path('admin_category_edit/<int:id>',views.admin_category_edit,name='admin_category_edit'),
    path('admin_delete_category/<int:id>/', views.admin_delete_category, name='admin_delete_category'),
    path('block_unblock_category/<int:id>/', views.block_unblock_category, name='block_unblock_category'),
    path('admin_varient/',views.admin_varient,name='admin_varient'),  
    path('admin_varient_add/',views.admin_varient_add,name='admin_varient_add'), 
    path('admin_varient_edit/<int:id>',views.admin_varient_edit,name='admin_varient_edit'), 
    path('admin_varient_delete/<int:id>',views.admin_varient_delete,name='admin_varient_delete'), 
    path('admin_provider_type/',views.admin_provider_type,name='admin_provider_type'), 
    path('admin_provider_type_insert/',views.admin_provider_type_insert,name='admin_provider_type_insert'),
    path('admin_provider_type_edit/<int:id>',views.admin_provider_type_edit,name='admin_provider_type_edit'),
    path('order/',views.order,name='order'),
    path('orderitems/<int:order_number>',views.orderitems,name='orderitems'),
    path('sales_report',views.sales_report,name='sales_report'),
    path('service-offers/',views.service_offers, name='service-offers'),
    path('create-service-offer/',views.create_service_offer, name='create-service-offer'),
    path('edit-service-offers/<int:id>',views.edit_service_offers, name='edit-service-offers'),
    path('delete-service-offer/<int:id>/',views.delete_service_offer, name='delete-service-offer'),
    path('category-offers/',views.category_offers, name='category-offers'),
    path('create-category-offer/',views.create_category_offer, name='create-category-offer'),
    path('edit-category-offers/<int:id>',views.edit_category_offers, name='edit-category-offers'), 
    path('delete-category-offer/<int:id>/',views.delete_category_offer, name='delete-category-offer'),
    path('admin_coupon/',views.admin_coupon,name='admin_coupon'),
    path('create_coupon/',views.create_coupon, name='create_coupon'),
    path('edit_coupon/<int:id>',views.edit_coupon,name='edit_coupon'),
    path('delete_coupon/<int:id>',views.delete_coupon,name='delete_coupon'),



















]