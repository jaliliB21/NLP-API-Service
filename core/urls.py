from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
 
    # JWT authentication URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Receive Access and Refresh tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Receive a new Access token using the Refresh token
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),   # Checking the validity of the token

    # include 'users' application URLs
    path('api/users/', include('users.urls')),
    
    # path('api/', include('nlp_services.urls')), 
]