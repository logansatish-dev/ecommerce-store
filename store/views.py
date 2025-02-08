from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Product, Category, Order, OrderItem
from .forms import SignupForm, ReviewForm
from django.apps import apps 
from django.db.models import Q


# Homepage
def home(request):
    return render(request, 'store/home.html')


# Product List Page
def product_list(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'store/product_list.html', {'products': products, 'categories': categories})


# Product Detail Page
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()  # Fetch all reviews for this product
    form = ReviewForm()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  # Assign logged-in user
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect('product_detail', product_id=product.id)

    return render(request, 'store/product_detail.html', {'product': product, 'reviews': reviews, 'form': form})


# Shopping Cart View
def cart_view(request):
    cart = request.session.get('cart', {})  
    cart_items = []

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        cart_items.append({'product': product, 'quantity': quantity})

    return render(request, 'store/cart.html', {'cart_items': cart_items})


# Add to Cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1  

    request.session['cart'] = cart  
    messages.success(request, f"{product.name} added to cart!")  

    return redirect('cart')  


# Remove from Cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart!")

    return redirect('cart')  


# Signup View
def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username, email, password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')
    return render(request, 'store/signup.html')


# Login View
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

# User Registration
def register_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Account created! Please log in.")
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'store/register.html', {'form': form})


@login_required
def checkout(request):
    Product = apps.get_model('store', 'Product')  # Dynamically get model

    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart')

    total_price = 0
    order = Order.objects.create(user=request.user, total_price=0)

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)  # Fetch product
            total_price += product.price * quantity
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
        except Product.DoesNotExist:
            messages.error(request, f"Product with ID {product_id} not found!")
            continue  # Skip missing products

    order.total_price = total_price
    order.save()

    request.session['cart'] = {}  # Clear cart after order placement
    messages.success(request, "Order placed successfully!")

    return redirect('order_success')  # Ensure 'order_success' URL exists


def order_success(request):
    return render(request, 'store/order_success.html')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})

def search_products(request):
    query = request.GET.get('q', '')  # Get search query from URL
    products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'store/product_list.html', {'products': products, 'query': query})
