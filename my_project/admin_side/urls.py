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












]