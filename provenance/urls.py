from django.urls import path
from . import views

urlpatterns = [
    # Provenance detail timeline
    path('<int:listing_id>/', views.provenance_detail, name='provenance_detail'),
    
    # Download certificate
    path('<int:listing_id>/certificate/', views.download_certificate, name='download_certificate'),
    
    # API for chain validation
    path('api/<int:listing_id>/validate/', views.validate_chain_api, name='validate_chain_api'),
]
