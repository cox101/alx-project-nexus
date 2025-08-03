from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .views import RegisterView

app_name = 'users'

# Add this class for a basic index view
class UserAPIRootView(APIView):
    def get(self, request):
        return Response({
            'register': request.build_absolute_uri('register/'),
            'token_refresh': request.build_absolute_uri('token/refresh/'),
        })

urlpatterns = [
    # Root URL - shows available endpoints
    path('', UserAPIRootView.as_view(), name='api-root'),
    
    # Registration endpoint
    path('register/', RegisterView.as_view(), name='register'),
    
    # JWT token refresh endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
