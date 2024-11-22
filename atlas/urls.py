from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'documents', views.DocumentViewSet)

urlpatterns = [
    path('search', views.SearchView.as_view(), name='atlas-search'),
    path('search/cost', views.SearchView.calculate_cost, name='calculate'),
    path('credits/buy', views.CreditsView.buy, name='atlas-credits-buy'),
    path('credits/apply', views.CreditsView.apply, name='atlas-credits-apply'),
    path('', include(router.urls)),
]
