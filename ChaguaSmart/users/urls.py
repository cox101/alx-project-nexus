from django.urls import path
from rest_framework.views import APIView  # Add this import
from rest_framework.response import Response  # Add this import
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
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
    
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
