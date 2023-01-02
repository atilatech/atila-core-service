from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'documents', views.DocumentViewSet)

urlpatterns = [
    path('search', views.SearchView.as_view(), name='atlas-search'),
    path('', include(router.urls)),
]
