from django.urls import path
from . import views

urlpatterns = [
    # Public marketplace
    path('feed/', views.marketplace_feed, name='marketplace_feed'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),
    
    # CRUD for listings (Generator only)
    path('create/', views.create_listing, name='create_listing'),
    path('listing/<int:listing_id>/delete/', views.delete_listing, name='delete_listing'),
    
    # API Endpoints
    path('api/calculate-price/', views.calculate_price_api, name='calculate_price_api'),
    path('api/verify/', views.mock_opencv_verification_api, name='opencv_verify_api'),
]
