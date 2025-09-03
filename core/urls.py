from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# these two imports 
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
 
    # JWT authentication URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Receive Access and Refresh tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Receive a new Access token using the Refresh token
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),   # Checking the validity of the token

    # include 'users' application URLs
    path('api/users/', include('users.urls')),
    
    # include 'nlp_services' application URLs
    path('api/nlp/', include('nlp_services.urls')), 
]

# This is for serving static files during development ONLY.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)