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


]

