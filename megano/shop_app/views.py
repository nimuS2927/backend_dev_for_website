import json

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    ListCreateAPIView,
    UpdateAPIView,
)
from django_filters import rest_framework as filters_rf
from rest_framework.filters import OrderingFilter

from .models import (
    Product,
    Category,
    Sale,
    Review,
    Tag,
    Order, ProductOptions,
)
from .serializers import (
    CategoriesSerializer,
    ProductSerializer,
    CatalogPagination,
    SaleSerializer,
    ProductIdSerializer,
    ReviewSerializer,
    TagSerializer,
    PaymentSerializer, OrderSerializer,
)
from .filters import ProductFilter, CustomOrderingFilter, CustomDjangoFilterBackend
from .basket import Basket


class CategoriesAPIView(ListAPIView):
    queryset = Category.objects.select_related('parent', 'image').filter(level=0)
    serializer_class = CategoriesSerializer


class CatalogAPIView(ListAPIView):
    queryset = Product.objects\
        .select_related('category')\
        .prefetch_related('images', 'tags', 'reviews').distinct()
    serializer_class = ProductSerializer
    pagination_class = CatalogPagination
    filter_backends = (CustomDjangoFilterBackend, CustomOrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ('rating', 'price_p', 'reviews', 'data_created')


class ProductsPopularAPIView(ListAPIView):
    queryset = Product.objects\
        .select_related('category')\
        .prefetch_related('images', 'tags', 'reviews')\
        .order_by('-quantity_sold', 'rating')[:10]
    serializer_class = ProductSerializer


class ProductsLimitedAPIView(ListAPIView):
    queryset = Product.objects\
        .select_related('category')\
        .prefetch_related('images', 'tags', 'reviews')\
        .order_by('count_p', '-rating')[:10]
    serializer_class = ProductSerializer


class SalesAPIView(ListAPIView):
    queryset = Sale.objects\
        .select_related('product')\
        .prefetch_related('product__images')\
        .order_by('data_from')\
        .filter(status=True)
    serializer_class = SaleSerializer
    pagination_class = CatalogPagination


class BannersAPIView(ListAPIView):
    queryset = Product.objects\
        .select_related('category')\
        .prefetch_related('images', 'tags', 'reviews').all()
    serializer_class = ProductSerializer


class ProductAPIView(RetrieveAPIView):
    queryset = Product.objects\
        .select_related('category')\
        .prefetch_related('images', 'tags', 'reviews', 'specifications')
    serializer_class = ProductIdSerializer


class ReviewsCreateAPIView(LoginRequiredMixin, CreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.request.query_params['id']
        queryset = Review.objects \
            .select_related('user') \
            .prefetch_related('product') \
            .filter(product__id=product_id)
        return queryset

    def post(self, request, *args, **kwargs):
        author = request.data.get('author')
        email = request.data.get('email')
        text = request.data.get('text')
        rate = int(request.data.get('rate'))
        product = Product.objects.get(pk=kwargs.get('pk'))
        review = Review.objects.create(
            user=request.user,
            product=product,
            text=text,
            rate=rate,
            )
        reviews = Review.objects.filter(product=product)
        serialized = ReviewSerializer(reviews, many=True)
        return Response(serialized.data, status=200)


class TagAPIView(ListAPIView):
    serializer_class = TagSerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        subcutegories_qs = Category.objects.filter(parent=category_id)
        if category_id:
            family_category = [int(category_id)]
            for subcategory in subcutegories_qs:
                family_category.append(subcategory.id)
            queryset = Tag.objects \
                .prefetch_related('products') \
                .filter(products__category__id__in=family_category)\
                .distinct()
        else:
            queryset = Tag.objects \
                .prefetch_related('products') \
                .all()
        return queryset


class PaymentAPIView(CreateAPIView):
    serializer_class = PaymentSerializer
    lookup_field = 'id'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            order = Order.objects.get(id=self.kwargs.get('id'))
            order.confirm_payment()
            return Response(status=200)
        else:
            return Response(status=404)


class BasketView(APIView):
    success_url = reverse_lazy('shop_app/basket')

    def get(self, request, *args, **kwargs):
        basket = Basket(request)
        products = Product.objects \
            .select_related('category') \
            .prefetch_related('images', 'tags', 'reviews') \
            .filter(id__in=map(int, basket.basket.keys()))
        data = []
        for product in products:

            image_list = []
            for image in product.images.all():
                image_list.append({'src': image.src.url,
                                   'alt': image.alt})

            tags_list = []
            for tag in product.tags.all():
                tags_list.append({'id': tag.id,
                                  'name': tag.name})

            product_data = {
                "id": product.id,
                "category": product.category.id,
                "price": basket.basket[str(product.id)]['price'],
                "count": basket.basket[str(product.id)]['count'],
                "date": product.data_created,
                "title": product.title,
                "description": product.description,
                "freeDelivery": product.free_delivery,
                "images": image_list,
                "tags": tags_list,
                "reviews": product.reviews.count(),
                "rating": product.rating,
            }
            data.append(product_data)

        return Response(data=data, status=200)

    def post(self, request, *args, **kwargs):
        basket = Basket(request)
        product_id = request.data.get('id')
        product_count = request.data.get('count')
        product = Product.objects.get(id=product_id)
        basket.add(product, product_count)
        products = Product.objects\
            .select_related('category')\
            .prefetch_related('images', 'tags', 'reviews')\
            .filter(id__in=map(int, basket.basket.keys()))
        data = []
        for product in products:

            image_list = []
            for image in product.images.all():
                image_list.append({'src': image.src.url,
                                   'alt': image.alt})

            tags_list = []
            for tag in product.tags.all():
                tags_list.append({'id': tag.id,
                                  'name': tag.name})

            product_data = {
                "id": product.id,
                "category": product.category.id,
                "price": basket.basket[str(product.id)]['price'],
                "count": basket.basket[str(product.id)]['count'],
                "date": product.data_created,
                "title": product.title,
                "description": product.description,
                "freeDelivery": product.free_delivery,
                "images": image_list,
                "tags": tags_list,
                "reviews": product.reviews.count(),
                "rating": product.rating,
            }
            data.append(product_data)

        return Response(data=data, status=200)

    def delete(self, request, *args, **kwargs):
        basket = Basket(request)
        product_id = request.data.get('id')
        product_count = request.data.get('count')
        basket.remove(product_id, product_count)
        products = Product.objects\
            .select_related('category')\
            .prefetch_related('images', 'tags', 'reviews')\
            .filter(id__in=map(int, basket.basket.keys()))
        data = []
        for product in products:

            image_list = []
            for image in product.images.all():
                image_list.append({'src': image.src.url,
                                   'alt': image.alt})

            tags_list = []
            for tag in product.tags.all():
                tags_list.append({'id': tag.id,
                                  'name': tag.name})

            product_data = {
                "id": product.id,
                "category": product.category.id,
                "price": basket.basket[str(product.id)]['price'],
                "count": basket.basket[str(product.id)]['count'],
                "date": product.data_created,
                "title": product.title,
                "description": product.description,
                "freeDelivery": product.free_delivery,
                "images": image_list,
                "tags": tags_list,
                "reviews": product.reviews.count(),
                "rating": product.rating,
            }
            data.append(product_data)

        return Response(data=data, status=200)


class OrderView(ListAPIView, CreateAPIView):
    serializer_class = OrderSerializer
    login_url = '/sign-in/'

    def get_queryset(self, *args, **kwargs):
        return Order.objects \
            .select_related('user') \
            .prefetch_related('products_in_order',
                              'options',
                              'products_in_order__images',
                              'products_in_order__tags',
                              'products_in_order__reviews') \
            .filter(user=self.request.user, status='accepted')

    def post(self, request, *args, **kwargs):
        p_options = []
        id_list = []
        for item in request.data:
            p_id = item.get('id')
            p_price = item.get('price')
            p_count = item.get('count')
            p_options.append({
                p_id: {
                    'price_option': p_price,
                    'count_option': p_count
                }
            })
            id_list.append(p_id)
        products = Product.objects.filter(id__in=id_list)
        order = Order.objects.create(
            user=request.user,
            status='accepted',
        )

        order.products_in_order.set(products)
        order.save()
        for product in p_options:
            for key, value in product.items():
                product_options = ProductOptions.objects.create(
                    id_product=key,
                    price_option=value.get('price_option'),
                    count_option=value.get('count_option'),
                    order=order,
                    product=products.get(id=key),
                )
        return Response(status=200, data={"orderId": order.id})


class OrderIDView(RetrieveAPIView, CreateAPIView, UpdateAPIView):
    serializer_class = OrderSerializer
    lookup_field = 'id'

    def get_queryset(self, *args, **kwargs):
        return Order.objects \
            .select_related('user') \
            .prefetch_related('products_in_order',
                              'options',
                              'products_in_order__images',
                              'products_in_order__tags',
                              'products_in_order__reviews') \
            .filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        city = request.data.get('city')
        address = request.data.get('address')
        delivery_type = request.data.get('deliveryType')
        payment_type = request.data.get('paymentType')
        if city:
            order.city = city
        if address:
            order.address = address
        if delivery_type:
            order.delivery_type = delivery_type
        if payment_type:
            order.payment_type = payment_type
        order.save()
        serializer = self.serializer_class(order)
        print(serializer.data)
        data = serializer.data
        data['orderId'] = order.id
        return Response(data=data, status=200)
