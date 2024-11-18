from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'documents', views.DocumentViewSet)

urlpatterns = [
    path('search', views.SearchView.as_view(), name='atlas-search'),
    path('payment', views.PaymentView.as_view(), name='atlas-payment'),
    path('search/cost', views.SearchView.calculate_cost, name='calculate'),
    path('', include(router.urls)),
]
