from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from shop import views as shop_views, views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # np. http://127.0.0.1:8000/
    path('', views.home, name='home'),

    # np. http://127.0.0.1:8000/sell/
    path('sell/', views.sell_view, name='sell'),

    # np. http://127.0.0.1:8000/signup/
    path('signup/', views.signup, name='signup'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('approve-product/<int:product_id>/', views.approve_product, name='approve_product'),

    path('browse/', views.browse_products, name='browse_products'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('user-panel/', views.user_panel, name='user_panel'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('cart/add/<int:item_id>/', views.add_quantity, name='cart_add'),
    path('cart/subtract/<int:item_id>/', views.subtract_quantity, name='cart_subtract'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='cart_remove'),
    path('reject/<int:product_id>/', views.reject_product, name='reject_product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]

