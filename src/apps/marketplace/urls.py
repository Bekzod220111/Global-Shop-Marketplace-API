from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    CategoryListCreateView, CategoryDetailView,
    ProductListCreateView, ProductDetailView,
    OrderListCreateView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/categories/', CategoryListCreateView.as_view()),
    path('api/categories/<int:pk>/', CategoryDetailView.as_view()),
    path('api/products/', ProductListCreateView.as_view()),
    path('api/products/<int:pk>/', ProductDetailView.as_view()),
    path('api/orders/', OrderListCreateView.as_view()),
]