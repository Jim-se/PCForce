from .models import CartItem, Product, User, Review, Order, OrderItem, Category
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomerSignUpForm, ProductForm, ReviewForm, CategoryForm
from django.db.models import Q, Avg
from django.http import JsonResponse

def home(request):
    last_search = request.session.get('last_search')
    recommended_products = Product.objects.none()
    recommendation_text = ''

    if last_search:
        recommended_products = Product.objects.annotate(average_rating=Avg('review__rating')).order_by('-average_rating')

        query = last_search.get('q')
        category = last_search.get('category')
        brand = last_search.get('brand')
        min_price = last_search.get('min_price')
        max_price = last_search.get('max_price')
        in_stock = last_search.get('in_stock')

        recommendation_parts = []

        if query:
            recommendation_parts.append(f'search "{query}"')

        if category:
            category_name = Category.objects.filter(id=category).values_list('name', flat=True).first()
            if not category_name:
                category_name = category
            recommendation_parts.append(f'category "{category_name}"')

        if brand:
            recommendation_parts.append(f'brand "{brand}"')

        if min_price:
            recommendation_parts.append(f'min price {min_price}')

        if max_price:
            recommendation_parts.append(f'max price {max_price}')

        if in_stock:
            recommendation_parts.append('in-stock products')

        recommendation_text = 'Based on your last search: ' + ', '.join(recommendation_parts)


        if query:
            recommended_products = recommended_products.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(category__name__icontains=query) |
                Q(code__icontains=query) |
                Q(description__icontains=query)
            )

        if category:
            recommended_products = recommended_products.filter(category_id=category)

        if brand:
            recommended_products = recommended_products.filter(brand__icontains=brand)

        if min_price:
            recommended_products = recommended_products.filter(price__gte=min_price)

        if max_price:
            recommended_products = recommended_products.filter(price__lte=max_price)

        if in_stock:
            recommended_products = recommended_products.filter(stock__gt=0)

        recommended_products = recommended_products[:4]

    return render(request, 'home.html', {
        'recommended_products': recommended_products,
        'recommendation_text': recommendation_text
    })

def product_details(request, product_id):
    product = Product.objects.get(uuid=product_id)
    reviews = Review.objects.filter(product=product)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    has_reviewed = False

    if request.user.is_authenticated:
        has_reviewed = Review.objects.filter(
            product=product,
            user=request.user
        ).exists()

    return render(request, 'product_details.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'has_reviewed': has_reviewed
    })

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def products(request):
    products = Product.objects.annotate(average_rating=Avg('review__rating'))
    categories = Category.objects.all().order_by('name')

    query = request.GET.get('q')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    in_stock = request.GET.get('in_stock')
    sort = request.GET.get('sort')

    if query or category or brand or min_price or max_price or in_stock:
        request.session['last_search'] = {
            'q': query,
            'category': category,
            'brand': brand,
            'min_price': min_price,
            'max_price': max_price,
            'in_stock': in_stock,
        }

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__name__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query)
        )

    if category:
        products = products.filter(category_id=category)

    if brand:
        products = products.filter(brand__icontains=brand)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if in_stock:
        products = products.filter(stock__gt=0)

    if sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'products.html', {
        'products': products,
        'query': query,
        'selected_category': category,
        'brand': brand,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
        'sort': sort,
        'categories': categories,
    })

def auth(request):
    if request.user.is_authenticated:
        return redirect('profile')

    signup_form = CustomerSignUpForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'signup':
            signup_form = CustomerSignUpForm(request.POST)

            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect('profile')

        elif form_type == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('profile')

            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth.html', {'signup_form': signup_form})

@login_required(login_url='auth')
def profile(request):
    users = None
    categories = None

    if request.user.user_type == 'owner':
        users = User.objects.exclude(id=request.user.id)
    if request.user.user_type in ['owner', 'employee']:
        categories = Category.objects.all().order_by('name')
    if request.user.user_type in ['owner', 'employee']:
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'profile.html', {
        'users': users,
        'orders': orders,
        'categories': categories,
    })


def logout_user(request):
    logout(request)
    return redirect('home')



@login_required(login_url='auth')
def add_product(request):
    if request.user.user_type not in ['owner', 'employee']:
        return redirect('products')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('products')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

@login_required(login_url='auth')
def make_employee(request, user_id):
    if request.user.user_type != 'owner':
        return redirect('profile')

    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        user.user_type = 'employee'
        user.save()

    return redirect('profile')

@login_required(login_url='auth')
def make_customer(request, user_id):
    if request.user.user_type != 'owner':
        return redirect('profile')

    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        user.user_type = 'customer'
        user.save()

    return redirect('profile')

@login_required(login_url='auth')
def add_to_cart(request, product_id):
    if request.user.user_type != 'customer':
        return redirect('products')

    product = Product.objects.get(uuid=product_id)

    if product.stock <= 0:
        messages.error(request, 'This product is out of stock.')
        return redirect('products')

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, 'You cannot add more than the available stock.')

    return redirect('products')

@login_required(login_url='auth')
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    total = 0

    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required(login_url='auth')
def remove_from_cart(request, product_id):
    if request.user.user_type != 'customer':
        return redirect('products')

    product = Product.objects.get(uuid=product_id)

    cart_item = CartItem.objects.filter(
        user=request.user,
        product=product
    ).first()

    if cart_item:
        cart_item.delete()

    return redirect('cart')

@login_required(login_url='auth')
def increase_cart_item(request, product_id):
    if request.user.user_type != 'customer':
        return redirect('products')

    product = Product.objects.get(uuid=product_id)

    cart_item = CartItem.objects.filter(
        user=request.user,
        product=product
    ).first()

    if not cart_item:
        return JsonResponse({'success': False, 'message': 'Item not found.'}, status=404)

    if cart_item.quantity < product.stock:
        cart_item.quantity += 1
        cart_item.save()
    else:
        return JsonResponse({
            'success': False,
            'message': 'You cannot add more than the available stock.'
        }, status=400)

    cart_total = 0
    for item in CartItem.objects.filter(user=request.user):
        cart_total += item.product.price * item.quantity

    item_subtotal = cart_item.product.price * cart_item.quantity

    return JsonResponse({
        'success': True,
        'quantity': cart_item.quantity,
        'item_subtotal': f'{item_subtotal:.2f}',
        'cart_total': f'{cart_total:.2f}'
    })

@login_required(login_url='auth')
def decrease_cart_item(request, product_id):
    if request.user.user_type != 'customer':
        return redirect('products')

    product = Product.objects.get(uuid=product_id)

    cart_item = CartItem.objects.filter(
        user=request.user,
        product=product
    ).first()

    if not cart_item:
        return JsonResponse({'success': False, 'message': 'Item not found.'}, status=404)

    removed = False

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        removed = True

    cart_total = 0
    for item in CartItem.objects.filter(user=request.user):
        cart_total += item.product.price * item.quantity

    if removed:
        return JsonResponse({
            'success': True,
            'removed': True,
            'cart_total': f'{cart_total:.2f}'
        })

    item_subtotal = cart_item.product.price * cart_item.quantity

    return JsonResponse({
        'success': True,
        'removed': False,
        'quantity': cart_item.quantity,
        'item_subtotal': f'{item_subtotal:.2f}',
        'cart_total': f'{cart_total:.2f}'
    })

@login_required(login_url='auth')
def delete_product(request, product_id):
    if request.user.user_type not in ['owner', 'employee']:
        return redirect('products')

    product = Product.objects.get(uuid=product_id)

    if request.method == 'POST':
        typed_name = request.POST.get('product_name')

        if typed_name == product.name:
            product.delete()
            return redirect('products')

        return render(request, 'delete_product.html', {
            'product': product,
            'error': 'Product name does not match.'
        })

    return render(request, 'delete_product.html', {
        'product': product
    })

@login_required(login_url='auth')
def edit_product(request, product_id):
    if request.user.user_type not in ['owner', 'employee']:
        return redirect('products')

    product = Product.objects.get(uuid=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            return redirect('product_details', product_id=product.uuid)
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {
        'form': form,
        'product': product
    })

@login_required(login_url='auth')
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('profile')

    return redirect('profile')

@login_required(login_url='auth')
def add_review(request, product_id):
    if request.user.user_type != 'customer':
        return JsonResponse({
            'success': False,
            'message': 'Only customers can review products.'
        }, status=403)

    product = Product.objects.get(uuid=product_id)

    if Review.objects.filter(product=product, user=request.user).exists():
        return JsonResponse({
            'success': False,
            'message': 'You have already reviewed this product.'
        }, status=400)

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            average_rating = Review.objects.filter(product=product).aggregate(
                Avg('rating')
            )['rating__avg']

            return JsonResponse({
                'success': True,
                'message': 'Review submitted successfully.',
                'rating': review.rating,
                'comment': review.comment,
                'username': request.user.username,
                'average_rating': round(average_rating, 1)
            })

        return JsonResponse({
            'success': False,
            'message': 'Rating must be between 1 and 5.'
        }, status=400)

    return redirect('product_details', product_id=product.uuid)

@login_required(login_url='auth')
def checkout(request):
    if request.user.user_type != 'customer':
        return redirect('products')

    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    order = Order.objects.create(
        user=request.user,
        total=total,
        status='completed'
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity
        )

        item.product.stock -= item.quantity
        item.product.save()

    cart_items.delete()

    messages.success(request, 'Checkout completed successfully.')
    return redirect('profile')

@login_required(login_url='auth')
def update_order_status(request, order_id):
    if request.user.user_type not in ['owner', 'employee']:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission.'
        }, status=403)

    order = Order.objects.get(id=order_id)

    if request.method == 'POST':
        status = request.POST.get('status')

        if status in ['pending', 'completed', 'cancelled']:
            order.status = status
            order.save()

            return JsonResponse({
                'success': True,
                'status': order.status,
                'status_display': order.get_status_display()
            })

        return JsonResponse({
            'success': False,
            'message': 'Invalid status.'
        }, status=400)

    return redirect('profile')

@login_required(login_url='auth')
def add_category(request):
    if request.user.user_type not in ['owner', 'employee']:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission.'
        }, status=403)

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            category = form.save()

            return JsonResponse({
                'success': True,
                'id': category.id,
                'name': category.name
            })

        return JsonResponse({
            'success': False,
            'message': 'Category name is invalid or already exists.'
        }, status=400)

    return redirect('profile')


@login_required(login_url='auth')
def edit_category(request, category_id):
    if request.user.user_type not in ['owner', 'employee']:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission.'
        }, status=403)

    category = Category.objects.get(id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            category = form.save()

            return JsonResponse({
                'success': True,
                'id': category.id,
                'name': category.name
            })

        return JsonResponse({
            'success': False,
            'message': 'Category name is invalid or already exists.'
        }, status=400)

    return redirect('profile')


@login_required(login_url='auth')
def delete_category(request, category_id):
    if request.user.user_type not in ['owner', 'employee']:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission.'
        }, status=403)

    category = Category.objects.get(id=category_id)

    if request.method == 'POST':
        category.delete()

        return JsonResponse({
            'success': True,
            'id': category_id
        })

    return redirect('profile')
