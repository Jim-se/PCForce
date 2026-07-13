from django.contrib import admin
from django.urls import path
from store import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.products, name='products'),
    path('auth/', views.auth, name='auth'),
    path('cart/', views.cart, name='cart'),
]
