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
    path('comment/approve/<int:comment_id>/', views.approve_comment, name='approve_comment'),
    path('comment/reject/<int:comment_id>/', views.reject_comment, name='reject_comment'),
    path('order/create/', views.create_order, name='create_order'),

    path('order/success/', views.order_success, name='order_success'),
    path('approve_order/<int:order_id>/', views.approve_order, name='approve_order'),
    path('reject_order/<int:order_id>/', views.reject_order, name='reject_order'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/toggle_hide/', views.toggle_hide_product, name='toggle_hide_product'),

    path('manage/product/<int:product_id>/hide/', views.hide_product_by_admin, name='hide_product_by_admin'),
    path('manage/product/<int:product_id>/restore/', views.restore_product_by_admin, name='restore_product_by_admin'),

]

