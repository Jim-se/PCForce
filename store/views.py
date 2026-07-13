from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def auth(request):
    return render(request, 'auth.html')

def cart(request):
    return render(request, 'cart.html')

def product_details(request):
    return render(request, 'product_details.html')

def products(request):
    return render(request, 'products.html')

def profile(request):
    return render(request, 'profile.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')