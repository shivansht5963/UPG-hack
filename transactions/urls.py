from django.urls import path
from . import views

urlpatterns = [
    # Create offer
    path('offer/<int:listing_id>/', views.create_offer, name='create_offer'),
    
    # Seller actions
    path('accept/<int:transaction_id>/', views.accept_offer, name='accept_offer'),
    path('reject/<int:transaction_id>/', views.reject_offer, name='reject_offer'),
    
    # Buyer actions
    path('pay/<int:transaction_id>/', views.create_razorpay_order, name='create_razorpay_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    
    # View offers
    path('my-offers/', views.buyer_offers, name='buyer_offers'),
    path('received-offers/', views.seller_offers, name='seller_offers'),
]
