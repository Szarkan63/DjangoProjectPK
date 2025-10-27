"""
URL configuration for DjangoProjectPK project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from DjangoProjectPK import settings
from shop import views as shop_views

urlpatterns = [
    # 1. Panel administratora
    path('admin/', admin.site.urls),

    # 2. Ścieżki uwierzytelniania (logowanie/wylogowanie) zgrupowane pod 'accounts/'
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # 3. Dołączenie wszystkich adresów z aplikacji 'shop'
    path('', include('shop.urls')),
]

# Konfiguracja do serwowania plików (np. obrazków) w trybie deweloperskim
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

