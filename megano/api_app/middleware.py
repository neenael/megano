import datetime
from django.utils.deprecation import MiddlewareMixin
from .models import Sale


class SaleMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/admin/"):
            time_now = datetime.date.today()
            unapplied_sales = Sale.objects.filter(is_applied=False)
            if unapplied_sales:
                for sale in unapplied_sales:
                    if sale.dateFrom <= time_now <= sale.dateTo:
                        print("sale in MW", sale)
                        sale.is_active = True
                    elif time_now <= sale.dateFrom <= sale.dateTo:
                        continue
                    else:
                        sale.delete()
                        continue
                    product = sale.product
                    sale.oldPrice = product.price
                    sale.is_applied = True
                    product.price = sale.salePrice
                    sale.save(update_fields=["oldPrice", "is_applied", "is_active"])
                    print("sale in mw", sale)
                    product.save(update_fields=["price"])

            active_sales = Sale.objects.filter(is_active=True)
            if active_sales:
                for sale in active_sales:
                    if not(sale.dateFrom <= time_now <= sale.dateTo):
                        product = sale.product
                        product.price = sale.oldPrice
                        product.save(update_fields=["price"])
                        sale.delete()

        response = self.get_response(request)
        return response
