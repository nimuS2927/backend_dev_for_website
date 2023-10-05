import django_filters
from django_filters.filterset import BaseFilterSet, FilterSetMetaclass
from django_filters.rest_framework import filterset
from django_filters import utils
from django.db import models
from .models import Product, Category
from rest_framework.filters import OrderingFilter


class CustomOrderingFilter(OrderingFilter):
    ordering_param = 'sort'
    ordering_type = 'sortType'

    def get_ordering(self, request, queryset, view):
        """
        Ordering is set by a comma delimited ?ordering=... query parameter.
        The `ordering` query parameter can be overridden by setting
        the `ordering_param` value on the OrderingFilter or by
        specifying an `ORDERING_PARAM` value in the API settings.
        """
        params = request.query_params.get(self.ordering_param)
        if params:
            fields = [param.strip() for param in params.split(',')]
            ordering = self.remove_invalid_fields(queryset, fields, view, request)
            if ordering:
                sort_type = request.query_params.get(self.ordering_type)
                if sort_type == 'dec':
                    return ['-%s' % field for field in ordering]
                return ordering

        # No ordering was included, or all the ordering fields were invalid
        return self.get_default_ordering(view)


class CustomBaseFilterSet(BaseFilterSet):
    def filter_queryset(self, queryset):
        """
        Filter the queryset with the underlying form's `cleaned_data`. You must
        call `is_valid()` or `errors` before calling this method.

        This method should be overridden if additional filtering needs to be
        applied to the queryset before it is cached.
        """
        for name, value in self.form.cleaned_data.items():
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(
                queryset, models.QuerySet
            ), "Expected '%s.%s' to return a QuerySet, but got a %s instead." % (
                type(self).__name__,
                name,
                type(queryset).__name__,
            )
        # uniq_id = []
        # for i in queryset:
        #     if i.id not in uniq_id:
        #         uniq_id.append(i.id)
        # new_queryset = Product.objects.filter(id__in=uniq_id)
        return queryset


class CustomDFFilterSet(CustomBaseFilterSet, metaclass=FilterSetMetaclass):
    pass


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class ProductFilter(CustomDFFilterSet):
    name = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    minPrice = django_filters.NumberFilter(field_name='price_p', lookup_expr='gte')
    maxPrice = django_filters.NumberFilter(field_name='price_p', lookup_expr='lte')
    freeDelivery = django_filters.BooleanFilter(field_name='free_delivery')
    available = django_filters.BooleanFilter(field_name='available')
    # category = django_filters.NumberFilter(field_name='category__id')
    category = NumberInFilter(field_name='category', lookup_expr='in')
    tags = NumberInFilter(field_name='tags', lookup_expr='in')

    class Meta:
        model = Product
        fields = [
            'name',
            'minPrice',
            'maxPrice',
            'freeDelivery',
            'available',
            'category',
            'tags'
        ]


class CustomRFFilterSet(CustomDFFilterSet):
    pass


class CustomDjangoFilterBackend(django_filters.rest_framework.DjangoFilterBackend):
    filterset_base = CustomRFFilterSet
    raise_exception = True

    def get_filterset_kwargs(self, request, queryset, view):
        data = request.query_params
        new_data = {}
        subcutegories_list = []
        for key, value in data.items():
            if 'filter[' in key:
                new_key = key[key.find('[') + 1:key.find(']')]
                new_data[new_key] = value
            if 'category' in key:
                subcutegories_qs = Category.objects.filter(parent=value)
                # print(subcutegories_qs)
                subcutegories_list.append(value)
                for subcategory in subcutegories_qs:
                    subcutegories_list.append(str(subcategory.id))
            else:
                new_data[key] = value

        new_data['tags'] = ','.join(data.getlist('tags[]'))
        # print(new_data)
        # print(subcutegories_list)
        new_data['category'] = ','.join(subcutegories_list)
        return {
            "data": new_data,
            "queryset": queryset,
            "request": request,
        }

    def filter_queryset(self, request, queryset, view):
        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            return queryset

        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        return filterset.qs
