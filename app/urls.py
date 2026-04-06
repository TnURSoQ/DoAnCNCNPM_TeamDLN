from django.contrib import admin
from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name="home"),  # Render home view
    path('register/', views.register, name="register" ),
    path('login/', views.loginPage, name="login" ),
    path('search/', views.search, name="search" ),
    path('category/', views.category, name="category" ),
    path('detail/', views.detail, name="detail" ),
    path('logout/', views.logoutPage, name="logout" ),
    path('cart/', views.cart, name="cart" ),
    path('checkout/', views.checkout, name="checkout" ),
    path('update_item/', views.updateItem, name="update_item" ),
    path('invoice/<int:id>/', views.invoice_detail, name='invoice_detail'),
    path('order-history/', views.order_history, name='order_history'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('payment/', views.payment, name='payment'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success, name='success'),
    path('api/products/', views.get_products, name='get_products'),
    path('api/products/create/', views.create_product, name='create_product'),
    path('api/products/delete/<int:pk>/', views.delete_product, name='delete_product'),
]

