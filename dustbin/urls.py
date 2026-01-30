"""
URL configuration for dustbin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize admin site
admin.site.site_header = "CircuTrade AI Administration"
admin.site.site_title = "CircuTrade AI Admin"
admin.site.index_title = "Welcome to CircuTrade AI Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # App URLs
    path('', include('dashboard.urls')),  # Landing page and dashboards
    path('accounts/', include('accounts.urls')),  # Authentication
    path('marketplace/', include('marketplace.urls')),  # Waste listings
    path('provenance/', include('provenance.urls')),  # Blockchain tracking
    path('transactions/', include('transactions.urls')),  # Purchases
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
