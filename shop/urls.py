from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/",views.product_detail, name='product_detail'),
    path("vendor/<int:pk>/",views.vendor_detail, name='vendor_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:item_id>/',views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('checkout-preview/', views.checkout_preview, name='checkout_preview'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    path('create-order/', views.create_order, name='create_order'),    
    path('addresses/', views.address_list, name='address_list'),
    path('address/add/', views.address_edit, name='address_add'),
    path('address/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('address/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('address/<int:pk>/set-default/', views.address_set_default, name='address_set_default'),
]