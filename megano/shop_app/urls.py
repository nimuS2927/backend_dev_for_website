from django.urls import path
from .views import (
    CategoriesAPIView,
    CatalogAPIView,
    ProductsPopularAPIView,
    ProductsLimitedAPIView,
    SalesAPIView,
    BannersAPIView,
    ProductAPIView,
    ReviewsCreateAPIView,
    TagAPIView,
    PaymentAPIView,
    BasketView,
    OrderView,
    OrderIDView,
)


app_name = 'shop_app'

urlpatterns = [
    path('categories/', CategoriesAPIView.as_view(), name='categories'),
    path('catalog/', CatalogAPIView.as_view(), name='catalog'),
    path('product/<int:pk>/', ProductAPIView.as_view(), name='products_id'),
    path('product/<int:pk>/reviews', ReviewsCreateAPIView.as_view(), name='products_id_review'),
    path('products/popular/', ProductsPopularAPIView.as_view(), name='products_popular'),
    path('products/limited/', ProductsLimitedAPIView.as_view(), name='products_limited'),
    path('sales/', SalesAPIView.as_view(), name='sales'),
    path('banners/', BannersAPIView.as_view(), name='banners'),
    path('tags/', TagAPIView.as_view(), name='tags'),
    path('payment/<int:id>', PaymentAPIView.as_view(), name='payment'),
    path('basket', BasketView.as_view(), name='basket'),
    path('orders', OrderView.as_view(), name='orders'),
    path('order/<int:id>', OrderIDView.as_view(), name='orders_detail'),
]
