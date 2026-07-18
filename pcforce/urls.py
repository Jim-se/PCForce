from django.contrib import admin
from django.urls import path
from store import views  
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('make-employee/<int:user_id>/', views.make_employee, name='make_employee'),
    path('make-customer/<int:user_id>/', views.make_customer, name='make_customer'),
    path('add-to-cart/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<uuid:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('products/<uuid:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<uuid:product_id>/delete/', views.delete_product, name='delete_product'),
    path('products/', views.products, name='products'),
    path('auth/', views.auth, name='auth'),
    path('cart/', views.cart, name='cart'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_user, name='logout'),
    path('products/add/', views.add_product, name='add_product'),
    path('cart/increase/<uuid:product_id>/', views.increase_cart_item, name='increase_cart_item'),
    path('cart/decrease/<uuid:product_id>/', views.decrease_cart_item, name='decrease_cart_item'),
    path('products/<uuid:product_id>/review/', views.add_review, name='add_review'),
    path('products/<uuid:product_id>/', views.product_details, name='product_details'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
