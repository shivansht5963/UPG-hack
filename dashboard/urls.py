from django.urls import path
from . import views

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # Role-based dashboards
    path('dashboard/generator/', views.generator_dashboard, name='generator_dashboard'),
    path('dashboard/buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('dashboard/worker/', views.worker_dashboard, name='worker_dashboard'),
    
    # Additional features
    path('provenance-vault/', views.provenance_vault, name='provenance_vault'),
    path('esg-report/', views.esg_report, name='esg_report'),
]
