"""atila URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from atila import views
from atila.views import AtilaTokenObtainPairView

atila_router = routers.DefaultRouter()
atila_router.register(r'users', views.UserViewSet)
atila_router.register(r'groups', views.GroupViewSet)


# Create a function that always returns an error to test Sentry error
def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', AtilaTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/atila/', include(atila_router.urls)),
    path('api/atlas/', include('atlas.urls')),
    path('api/userprofile/', include('userprofile.urls')),
    path('api/chatbot/', include('chatbot.urls')),
    path('sentry-debug/', trigger_error),
]
