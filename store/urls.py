from django.urls import path
from .views import product_list, product_detail, cart_view, add_to_cart, home, login_view, remove_from_cart, signup_view, logout_view, register_view, checkout, order_success, order_history, search_products

urlpatterns = [
    path('', home, name='home'),
    path('category/<slug:category_slug>/', product_list, name='product_by_category'),  # Category filter  
    path('products/', product_list, name='product_list'),  
    path('product/<int:product_id>/', product_detail, name='product_detail'),  
    path('cart/', cart_view, name='cart'),  
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('checkout/', checkout, name='checkout'),
    path('order-success/', order_success, name='order_success'),
    path('order-history/', order_history, name='order_history'),
    path('search/', search_products, name='search_products'),
]

