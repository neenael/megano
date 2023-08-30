import json
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db.models import Q, Count
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.paginator import Paginator
from .models import Sale
from .serializers import *
from django.db import transaction
from auth_app.models import Profile


def login_view(request: HttpRequest):
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'username' in data and 'password' in data:
            username = data.get('username')
            password = data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse(status=200)
        return HttpResponse(status=500)


def sign_up_view(request: HttpRequest):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)

            if data.get('username') and data.get('password') and data.get('name'):
                username = data.get('username')
                password = data.get('password')
                first_name = data.get('name')

                if User.objects.filter(username=username).exists():
                    return JsonResponse({'error': 'User with this username already exists'}, status=400)

                new_user = User.objects.create(username=username, password=make_password(password),
                                               first_name=first_name)
                new_profile = Profile.objects.create(user=new_user)

                new_user.save()
                new_profile.save()
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return HttpResponse(status=201)
            return HttpResponse(status=400)
    except Exception:
        return Response(status=500)


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponse(status=200)
    return HttpResponse(status=500)


class CategoriesViewSet(viewsets.ViewSet):
    def list(self, request: HttpRequest) -> Response:
        try:
            category_queryset = Category.objects.all()
            serializer = CategorySerializer(category_queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(status=500)


class CatalogViewSet(viewsets.ViewSet):
    def list(self, request: HttpRequest) -> Response:
        try:
            data = request.GET.dict()
            sort_param = data.get("sort")
            sort_type = data.get("sortType")
            if sort_type == "inc":
                sort_param = "-" + sort_param
            min_price_param = Q(price__gte=data.get("filter[minPrice]"))
            max_price_param = Q(price__lte=data.get("filter[maxPrice]"))
            filter_params = min_price_param & max_price_param
            if data.get("filter[freeDelivery]") == 'true':
                is_delivery_free_param = Q(freeDelivery=True)
                filter_params = filter_params & is_delivery_free_param
            if data.get("filter[available]") == "true":
                count_param = Q(count__gte=1)
                filter_params = filter_params & count_param
            if data.get("filter[name]"):
                name_param = Q(title__icontains=data.get("filter[name]"))
                filter_params = filter_params & name_param
            if data.get("tags[]"):
                tag_param = Q(tags__id=data.get("tags[]"))
                filter_params = filter_params & tag_param
            if data.get("category"):
                category_param = Q(category=data.get("category"))
                filter_params = filter_params & category_param
            if "reviews" in sort_param:
                queryset = Product.objects.annotate(num_related=Count('reviews')).filter(filter_params).order_by('-num_related')
            else:
                queryset = Product.objects.filter(filter_params).order_by(sort_param)

            items_per_page = int(data.get("limit", 20))
            paginator = Paginator(queryset, items_per_page)
            page_number = int(data.get("currentPage", 1))
            page = paginator.get_page(page_number)
            serializer = ProductShortSerializer(page.object_list, many=True)
            return Response({"items": serializer.data, "currentPage": page.number, "lastPage": paginator.num_pages})
        except Exception:
            return Response(status=500)


class PopularProductsViewSet(viewsets.ViewSet):
    def list(self, request: HttpRequest) -> Response:
        try:
            queryset = Product.objects.filter(Q(count__gt=0)).order_by("-sold")[:4]
            serializer = ProductShortSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(status=500)


class LimitedProductsViewSet(viewsets.ViewSet):
    def list(self, request: HttpRequest) -> Response:
        try:
            queryset = Product.objects.filter(is_limited=True).order_by('-price')
            serializer = ProductShortSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return HttpResponse(status=500)


class SalesViewSet(viewsets.ViewSet):
    def list(self, request):
        try:
            queryset = Sale.objects.filter(is_active=True)
            items = []
            for sale in queryset:
                product = sale.product
                id = product.pk
                price = sale.oldPrice
                salePrice = sale.salePrice
                date_from = sale.dateFrom
                date_to = sale.dateTo
                title = product.title
                images = product.images.all()
                images = ImageSerializer(images, many=True).data
                item = {
                    "id": id,
                    "price": price,
                    "salePrice": salePrice,
                    "dateFrom": date_from,
                    "dateTo": date_to,
                    "title": title,
                    "images": images
                }



                items.append(item)




            items_per_page = 20
            paginator = Paginator(items, items_per_page)
            page_number = int(request.query_params.get("currentPage"))
            page = paginator.get_page(page_number)

            data = {
                'items': page.object_list,
                'currentPage': request.query_params.get("currentPage"),
                'lastPage': paginator.num_pages,
            }
            print("Data in VIEW", data)

            return JsonResponse(data, safe=False)
        except Exception:
            return Response(status=500)


class BannersViewSet(viewsets.ViewSet):
    def list(self, request: HttpRequest) -> Response:
        try:
            categories = Category.objects.all()
            banner_items = []
            cat_i = 0
            while len(banner_items) < 3:
                category = categories[cat_i]
                cat_i += 1
                product = Product.objects.filter(category=category).order_by("-rating")[:1].first()
                banner_items.append(product)
            serializer = ProductShortSerializer(banner_items, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(status=500)


class BasketViewSet(viewsets.ViewSet):

    def list(self, request: HttpRequest) -> Response:
        try:
            if request.user.is_authenticated:
                resp = request.session.get("cart")
                if request.user.is_authenticated:
                    queryset = Basket.objects.filter(user=request.user)
                    serializer = BasketSerializer(queryset, many=True)
                    return Response(serializer.data)
                return Response(status=200)

            else:
                cart = request.session.get("cart")
                if cart:
                    products = []
                    for product_id, count in cart.items():
                        new_product = Basket.objects.create(
                            user=None,
                            product_id=product_id,
                            count=count
                        )
                        products.append(new_product)

                    serializer = BasketSerializer(products, many=True)
                    return Response(serializer.data)
                else:
                    return Response(status=200)
        except Exception:
            return Response(status=500)

    @action(detail=False, methods=['post'])
    def add_product(self,  request: HttpRequest):
        try:
            if request.user.is_authenticated:
                all_products = Basket.objects.filter(user=request.user).order_by('product')
                current_product = all_products.filter(product_id=request.data['id']).first()
                if current_product:
                    current_product.count += int(request.data.get("count"))
                else:
                    current_product = Basket.objects.create(
                        user=request.user,
                        product_id=request.data['id'],
                        count=request.data['count']
                    )
                    sale = Sale.objects.filter(product_id=request.data['id']).first()
                    if sale:
                        current_product.product.price = sale.salePrice
                        current_product.product.save()

                current_product.save()
                serializer = BasketSerializer(all_products, many=True)
                return JsonResponse(serializer.data, safe=False)
            else:
                cart = request.session.get("cart", {})
                if str(request.data.get("id")) in cart.keys():
                    cart[str(request.data["id"])] += int(request.data["count"])
                else:
                    cart[str(request.data["id"])] = int(request.data["count"])
                request.session["cart"] = cart
                products = []
                for product_id, count in cart.items():
                    new_product = Basket.objects.create(
                        user=None,
                        product_id=product_id,
                        count=count
                    )
                    new_product.save()
                    products.append(new_product)
                serializer = BasketSerializer(products, many=True)
                return Response(serializer.data)
        except Exception:
            return Response(status=500)

    @action(detail=False, methods=['delete'])
    def delete_product(self, request: HttpRequest):
        try:
            if request.user.is_authenticated:
                data = json.loads(request.body)
                all_products = Basket.objects.filter(user=request.user).order_by('product')
                current_product = all_products.filter(product_id=data['id']).first()

                if current_product:
                    current_product.count -= data.get("count")
                    if current_product.count <= 0:
                        current_product.delete()
                    else:
                        current_product.save()
                serializer = BasketSerializer(all_products, many=True)
                return JsonResponse(serializer.data, safe=False)
            else:
                cart = request.session.get("cart", {})
                data = json.loads(request.body)

                if str(data.get("id")) in cart.keys():
                    cart[str(data["id"])] -= data["count"]
                    if cart[str(data["id"])] <= 0:
                       del cart[str(data["id"])]
                request.session["cart"] = cart
                products = []
                for product_id, count in cart.items():
                    new_product = Basket.objects.create(
                        user=None,
                        product_id=product_id,
                        count=count
                    )
                    new_product.save()
                    products.append(new_product)
                serializer = BasketSerializer(products, many=True)
                return Response(serializer.data)
        except Exception:
            return Response(status=500)


class OrdersViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        try:
            queryset = Order.objects.get(pk=pk)
            serializer = OrderSerializer(queryset)
            return Response(serializer.data)
        except Exception:
            return Response(status=500)

    def create(self, request):
        try:
            data = request.data
            is_lack = all([(Product.objects.filter(id=cart_item.get("id")).values("count").first().get("count") -
                            cart_item.get("count")) < 0 for cart_item in data])
            if is_lack:
                return Response(status=405)
            new_order = Order.objects.create()
            if request.user.is_authenticated:
                user = request.user.profile
                new_order.fullName = user.fullName
                new_order.email = user.email
                new_order.phone = user.phone
            products_list = []
            for item in data:
                new_order_product = OrderProduct.objects.create(
                    product_id=item.get("id"),
                    count=item.get("count"),
                    price=item.get("price")
                )
                products_list.append(new_order_product)
            new_order.products.set(products_list)
            new_order.save()
            return Response({"orderId": new_order.id})
        except Exception:
            return Response(status=500)

    def list(self, request):
        try:
            queryset = OrderHistory.objects.filter(user_id=request.user.id)
            serializer = OrderHistorySerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return HttpResponse(status=500)

    @action(detail=True,methods=["post"])
    def add_order_info(self, request: HttpRequest, pk: int = None) -> Response:
        try:
            data = request.data
            order = Order.objects.get(pk=pk)
            order.fullName = data.get("fullName")
            order.email = data.get("email")
            order.phone = data.get("phone")

            if data.get("deliveryType"):
                order.deliveryType = data["deliveryType"]
            else:
                order.deliveryType = "ordinary"
            if data.get("paymentType"):
                order.paymentType = data["paymentType"]
            else:
                order.paymentType = "online"
            if data.get("totalCost"):
                order.totalCost = data["totalCost"]
            else:
                total_cost = 0
                for product in data.get("products"):
                    total_cost += float(product.get("price")) * int(product.get("count"))
                order.totalCost = total_cost
            if data.get("status"):
                order.status = data["status"]
            else:
                order.status = "created"
            order.city = data.get("city")
            order.address = data.get("address")
            order.save()
            return Response({"orderId": order.id}, status=201)
        except Exception:
            return HttpResponse(status=500)


def card_validate(name, number, year, month, code):
    valid_name = len(name) > 0 and 2 <= len(name.split()) <= 3
    valid_number = len(number) == 16 and all(char.isdigit() for char in number)
    valid_year = len(year) == 2 and all(char.isdigit() for char in year)
    valid_month = len(month) == 2 and all(char.isdigit() for char in month)
    valid_code = len(code) == 3 and all(char.isdigit() for char in code)
    return valid_name and valid_number and valid_year and valid_month and valid_code


class PaymentViewSet(viewsets.ViewSet):
    @action(detail=True, methods=["post"])
    def payment(self, request: HttpRequest, pk: int = None) -> Response:
        try:
            with transaction.atomic():
                data = request.data
                if card_validate(**data):
                    queryset = Basket.objects.filter(user_id=request.user.id)
                    for basket in queryset:
                        product = basket.product
                        if product.count - basket.count >= 0:
                            product.count -= basket.count
                            product.sold += basket.count
                            product.save(update_fields=["count", "sold"])
                            basket.delete()
                        else:
                            return Response(status=405)
                    order = Order.objects.get(pk=pk)
                    order.status = "Paid"
                    history = OrderHistory.objects.create(user_id=request.user.id, order_id=order.id)
                    order.save(update_fields=["status"])
                    history.save()
                    return Response(status=200)
                return Response(status=405)
        except:
            return Response(status=500)


class ProfileViewSet(viewsets.ViewSet):
    def retrieve(self, request: HttpRequest, pk:int=None) -> Response:
        try:
            user = User.objects.get(pk=request.user.pk)
            profile = Profile.objects.get(user=user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Exception:
            return Response(status=500)

    @action(detail=False, methods=['post'])
    def add_info(self, request: HttpRequest):
        try:
            data = request.data
            user = User.objects.get(pk=request.user.pk)
            profile = Profile.objects.get(user=user)

            profile.fullName = data.get('fullName')
            profile.email = data.get('email')
            profile.phone = data.get('phone')
            if data.get('avatar'):
                profile.avatar = Image.objects.get(src=data.get('avatar').get('src'))
            else:
                profile.avatar = None

            profile.save()
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Exception:
            return Response(status=500)


class SetPasswordViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def set_password(self, request: HttpRequest) -> Response:
        try:
            data = request.data
            in_pass = data.get('currentPassword')
            user = request.user
            if user.is_authenticated:
                if user.check_password(in_pass):
                    user.password = make_password(data.get('newPassword'))
                    user.save(update_fields=["password"])
                    return Response(status=200)
                return Response(status=500)
        except Exception:
            return Response(status=500)


class AvatarViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def set_avatar(self, request: HttpRequest) -> Response:
        try:
            data = request.data.get("avatar")
            path = default_storage.save('avatars/{pk}/'.format(pk=request.user.pk) + data.name, data)
            file_url = settings.MEDIA_URL + path
            image = Image.objects.create(src=file_url, alt="avatar")
            image.save()
            profile = Profile.objects.get(user=request.user)
            profile.avatar = image
            profile.save()
            serializer = ImageSerializer(image)
            return Response(serializer.data)
        except Exception:
            return Response(status=500)


class TagsViewSet(viewsets.ViewSet):
    def list(self, request: HttpRequest) -> Response:
        try:
            data = request.query_params
            if data.get("category"):
                tags_queryset = Product.objects.filter(category_id=int(data.get("category"))).values_list('tags', flat=True)
                tags = []
                for tag_id in set(tags_queryset):
                    tag = get_object_or_404(Tag, id=tag_id)
                    if tag:
                        tags.append(tag)
            else:
                tags = Tag.objects.all()
            serializer = TagSerializer(tags, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(status=500)


class ProductViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None) -> Response:
        try:
            item = get_object_or_404(Product, pk=pk)
            serializer = ProductFullSerializer(item)
            return Response(serializer.data)
        except Exception:
            return HttpResponse(status=500)


class ReviewViewSet(viewsets.ViewSet):
    @action(detail=True, methods=["post"])
    def add_review(self, request: HttpRequest, pk: int) -> Response:
        try:
            data = request.data
            product = Product.objects.get(pk=pk)
            new_review = Review.objects.create(author=data.get("author"),
                                               email=data.get("email"),
                                               text=data.get("text"),
                                               rate=int(data.get("rate")))

            product.reviews.add(new_review)
            all_ratings = product.reviews.values_list('rate', flat=True)
            updated_rating = round(sum(all_ratings) / all_ratings.count(), 1)
            if updated_rating > 5:
                updated_rating = 5
            product.rating = updated_rating

            rating_specification = product.specifications.filter(name="Rating").first()
            if rating_specification:
                rating_specification.value = product.rating
                rating_specification.save()
            else:
                new_rating_specification = Specification.objects.create(
                    name="Рейтинг",
                    value=product.rating
                )
                product.specifications.add(new_rating_specification)
            new_review.save()
            product.save()
            queryset = product.reviews

            serializer = ReviewSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(status=500)
