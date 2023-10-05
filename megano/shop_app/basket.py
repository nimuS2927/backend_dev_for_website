from decimal import Decimal
from django.conf import settings
from rest_framework.request import Request


from .models import Product, Sale


class Basket(object):

    def __init__(self, request: Request):
        """
        Initial basket
        """
        self.session = request.session
        basket = self.session.get(settings.BASKET_SESSION_ID)
        if not basket:
            basket = self.session[settings.BASKET_SESSION_ID] = {}
        self.basket = basket

    def __iter__(self):
        """
        Iterating the item in the basket
        """
        products = Product.objects.filter(id__in=self.basket.keys())
        basket = self.basket.copy()
        for product in products:
            basket[str(product.id)]['product'] = product

        for item in basket.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['count']
            yield item

    def __len__(self):
        return sum(item['count'] for item in self.basket.values())

    def add(self, product: Product, count=1, update_count=False):
        """
        Adding or updating an item in the basket
        """
        try:
            sale = Sale.objects.get(product=product, status=True)
            price = sale.sale_price
        except Exception:
            price = product.price_p
        product_id = str(product.id)
        if product_id not in self.basket:
            self.basket[product_id] = {
                'count': 0,
                'price': str(price),
            }
        if update_count:
            self.basket[product_id]['count'] = count
        else:
            self.basket[product_id]['count'] += count
        self.save()

    def save(self):
        """
        Saving the item
        """
        self.session.modified = True

    def remove(self, product_id: int, count=1):
        """
        Remove item from basket
        """
        s_product_id = str(product_id)
        if s_product_id in self.basket:
            if count == self.basket[s_product_id]['count']:
                del self.basket[s_product_id]
            else:
                self.basket[s_product_id]['count'] -= count
            self.save()

    def get_total_price(self):
        return sum(Decimal(item['price']) for item in self.basket.values())

    def clear(self):
        del self.session[settings.BASKET_SESSION_ID]
        self.save()

    def get_product_id(self):
        return [int(product) for product in self.basket.keys()]
