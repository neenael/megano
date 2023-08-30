import datetime
import json
import os
import django
from django.contrib.auth.hashers import make_password
from django.test import TestCase, RequestFactory
from django.urls import reverse
from auth_app.models import Profile
from api_app.models import Category, Image, Sale, Order, OrderHistory, Tag, Product
from django.contrib.auth.models import User


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "megano.settings")
django.setup()


class SignUpTestCase(TestCase):

    def setUp(self):
        self.url = reverse('api_app:sign-up')

    def test_sign_up_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'name': 'Test User',
        }

        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(User.objects.get(username='testuser').check_password('testpassword'))

    def test_sign_up_existing_user(self):
        User.objects.create(username='testuser', password=make_password('password'))

        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'name': 'Test User',
        }

        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'User with this username already exists'})

    def test_sign_up_invalid_data(self):
        data = {
            'username': 'testuser',
            'name': 'Test User',
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username='testuser').exists())


class SignInTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.url = reverse('api_app:sign-in')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_successful_sign_in(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.login(username='testuser', password='testpassword'))

    def test_invalid_sign_in(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertFalse(self.client.login(username='testuser', password='wrongpassword'))

    def test_not_enough_data_sign_in(self):
        data = {
            'username': 'testuser',
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertFalse(self.client.login(username='testuser'))


class SignOutTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.url = reverse("api_app:log-out")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_log_out_success(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

    def test_log_out_unauthorized(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 500)


class CategoriesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.img = Image.objects.create(src="pic_path", alt="test pic")
        cls.category = Category.objects.create(title="Test Category", image=cls.img)

    @classmethod
    def tearDownClass(cls):
        cls.category.delete()
        cls.img.delete()

    def test_categories_create(self):
        print("Из Бд", Category.objects.get(title="Test Category", image=self.img).id)
        print("Из теста", self.category.id)
        print("Все вообще", Category.objects.all())
        self.assertEqual(self.category.image, Image.objects.get(src="pic_path", alt="test pic"))
        self.assertEqual(self.category, Category.objects.get(title="Test Category", image=self.img))

    def test_get_categories_list(self):
        response = self.client.get(reverse("api_app:categories"))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content[0].get("title"), 'Test Category')
        self.assertEqual(content[0].get("image").get("src"), 'pic_path')
        self.assertEqual(content[0].get("image").get("alt"), 'test pic')


class CatalogTestCase(TestCase):
    fixtures = ["fixtures/images_fixtures.json", "fixtures/categories_fixtures.json", "fixtures/catalog_fixture.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse("api_app:catalog")

    def test_list_view(self):
        request_data = {
            'sort': 'price',
            'sortType': '',
            'filter[minPrice]': '5',
            'filter[maxPrice]': '25',
            'filter[freeDelivery]': 'false',
            'filter[available]': 'false',
            'filter[name]': 'Product',
            'tags[]': '',
            'category': '',
            "currentPage": 1,
            "limit": 100,
        }

        response = self.client.get(self.url, data=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['items']), 2)  # Должно вернуться 2 товара
        self.assertEqual(response.data['items'][0]['title'], 'Product 1')  # Проверка имени продукта
        self.assertEqual(response.data['items'][1]['title'], 'Product 2')  # Проверка имени продукта

    def test_filter_view(self):
        request_data = {
            'sort': 'price',
            'sortType': 'inc',
            'filter[minPrice]': '5',
            'filter[maxPrice]': '25',
            'filter[freeDelivery]': 'true',
            'filter[available]': 'false',
            'filter[name]': 'Product',
            'tags[]': '',
            'category': '1',
            "currentPage": 1,
            "limit": 100,
        }

        response = self.client.get(self.url, data=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['items']), 1)  # Должен вернуться 1 товар
        self.assertEqual(response.data['items'][0]['title'], 'Product 1')  # Проверка имени продукта


class PopularProductsTestCase(TestCase):
    fixtures = ["fixtures/images_fixtures.json", "fixtures/categories_fixtures.json", "fixtures/catalog_fixture.json"]

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.url = reverse('api_app:popular-products')
        self.client.force_login(self.user)

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()

    def test_popular_products(self):
        response = self.client.get(self.url)
        data = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(data[0]['title'], 'Product 1')  # Проверка имени продукта

        product_2 = Product.objects.get(title="Product 2")
        product_2.sold = 30
        product_2.save(update_fields=["sold"])

        response = self.client.get(self.url)
        data = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(data[0]['title'], 'Product 2')  # Проверка имени продукта


class SaleTestCase(TestCase):
    fixtures = ["fixtures/images_fixtures.json", "fixtures/categories_fixtures.json", "fixtures/catalog_fixture.json"]

    def setUp(self):
        self.sale = Sale.objects.create(
            product_id=1,
            salePrice=2,
            dateFrom=datetime.datetime.now(),
            dateTo=datetime.datetime.now() + datetime.timedelta(days=1)
        )
        self.sale.save()

    def test_sale_success(self):
        response = self.client.get(reverse("api_app:sales"), {"currentPage": 1})
        print("response", response)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["items"][0]['title'], "Product 1")
        product = Product.objects.get(id=1)
        self.assertEqual(product.price, 2)
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.is_active, True)
        self.assertEqual(self.sale.is_applied, True)


class BasketViewSetTest(TestCase):
    fixtures = ["fixtures/images_fixtures.json", "fixtures/categories_fixtures.json", "fixtures/catalog_fixture.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_add_item_and_list_unauthenticated(self):
        response = self.client.post(reverse('api_app:basket'), data={"id": 1, "count": 2})
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)

        self.assertEqual(content[0]["id"], 1)
        self.assertEqual(content[0]["count"], 2)

        response = self.client.get(reverse('api_app:basket'))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)

        self.assertEqual(content[0]["id"], 1)
        self.assertEqual(content[0]["count"], 2)

    def test_add_item_and_list_authenticated(self):
        response = self.client.post(reverse('api_app:basket'), data={"id": 1, "count": 3})
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content[0]["id"], 1)
        self.assertEqual(content[0]["count"], 3)

        response = self.client.get(reverse('api_app:basket'))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content[0]["id"], 1)
        self.assertEqual(content[0]["count"], 3)

    def test_list_unauthenticated_empty_cart(self):
        response = self.client.get(reverse('api_app:basket'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')

    def test_list_authenticated_empty_cart(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('api_app:basket'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])


class OrdersTestCase(TestCase):
    fixtures = ["fixtures/images_fixtures.json", "fixtures/categories_fixtures.json", "fixtures/catalog_fixture.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile = Profile.objects.create(user=self.user)

    def test_create_order_success(self):
        basket = self.client.post(reverse('api_app:basket'), data={"id": 1, "count": 2}).content
        response = self.client.post(reverse('api_app:orders'), data=basket, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content)
        queryset = Order.objects.filter(id=response_content['orderId'])
        self.assertTrue(queryset.exists())
        new_order = queryset.first()
        new_order_product = new_order.products.all().first()
        self.assertEqual(new_order_product.product.title, "Product 1")
        self.assertEqual(new_order_product.count, 2)
        self.assertEqual(new_order_product.price, new_order_product.product.price)

    def test_create_order_failed_lack(self):
        basket = self.client.post(reverse('api_app:basket'), data={"id": 2, "count": 10}).content
        response = self.client.post(reverse('api_app:orders'), data=basket, content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_retrieve_order(self):
        basket = self.client.post(reverse('api_app:basket'), data={"id": 1, "count": 2}).content
        print("basket", basket)

        order_id = json.loads(self.client.post(
            reverse('api_app:orders'), data=basket, content_type='application/json').content).get("orderId")
        response = self.client.get(reverse('api_app:order', kwargs={'pk': order_id}))
        print("response", response.content)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        product = content["products"][0]
        self.assertEqual(product.get("title"), "Product 1")
        self.assertEqual(product.get("id"), 1)
        self.assertEqual(product.get("count"), 2)

    def test_list_order(self):
        self.client.force_login(self.user)
        basket = self.client.post(reverse('api_app:basket'), data={"id": 1, "count": 2}).content
        new_order = json.loads(
            self.client.post(
                reverse('api_app:orders'), data=basket, content_type='application/json'
            ).content
        )
        data = {
            'fullName': 'John Doe',
            'email': 'john@example.com',
            'phone': '+123456789',
            'deliveryType': 'express',
            'paymentType': 'online',
            'totalCost': 100.,
            'status': 'test',
            'city': 'New York',
            'address': '123 Main St'
        }
        new_order_id = json.loads(self.client.post(
            reverse("api_app:order", kwargs={"pk": new_order.get("orderId")}), data=data).content)
        OrderHistory.objects.create(user=self.user, order_id=new_order_id.get("orderId"))
        response_list = self.client.get(reverse('api_app:orders'))
        self.assertEqual(response_list.status_code, 200)
        content = json.loads(response_list.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0].get("fullName"), "John Doe")
        self.assertEqual(content[0].get("products")[0].get("id"), 1)

    def test_add_order_info(self):
        basket = self.client.post(reverse('api_app:basket'), data={"id": 1, "count": 2}).content
        new_order = json.loads(
            self.client.post(
                reverse('api_app:orders'), data=basket, content_type='application/json'
            ).content
        )
        data = {
            'fullName': 'John Doe',
            'email': 'john@example.com',
            'phone': '+123456789',
            'deliveryType': 'express',
            'paymentType': 'online',
            'totalCost': 100.,
            'status': 'test',
            'city': 'New York',
            'address': '123 Main St'
        }
        response_add_info = self.client.post(reverse("api_app:order", kwargs={"pk": new_order.get("orderId")}),
                                             data=data)
        self.assertEqual(response_add_info.status_code, 201)

        response_retrieve = self.client.get(reverse("api_app:order", kwargs={"pk": new_order.get("orderId")}))

        content = json.loads(response_retrieve.content)

        self.assertEqual(content.get("fullName"), data.get("fullName"))
        self.assertEqual(content.get("email"), data.get("email"))
        self.assertEqual(content.get("phone"), data.get("phone"))
        self.assertEqual(content.get("deliveryType"), data.get("deliveryType"))
        self.assertEqual(float(content.get("totalCost")), data.get("totalCost"))
        self.assertEqual(content.get("status"), data.get("status"))
        self.assertEqual(content.get("city"), data.get("city"))
        self.assertEqual(content.get("address"), data.get("address"))
        self.assertEqual(content.get("paymentType"), data.get("paymentType"))


class PaymentTestCase(TestCase):
    fixtures = ["fixtures/images_fixtures.json", "fixtures/categories_fixtures.json", "fixtures/catalog_fixture.json"]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        basket = self.client.post(reverse('api_app:basket'), data={"id": 1, "count": 2}).content
        self.order_id = json.loads(self.client.post(
            reverse('api_app:orders'), data=basket, content_type='application/json').content).get("orderId")

    def test_payment_success(self):
        self.client.force_login(self.user)
        payment_data = {
            "name": "Megano Payment Tester",
            "number": "1234567891234567",
            "year": "99",
            "month": "12",
            "code": "123",
        }
        response = self.client.post(reverse('api_app:payment', kwargs={"pk": self.order_id}),
                                    data=payment_data, content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_payment_invalid_data(self):
        self.client.force_login(self.user)
        payment_data = {
            "name": "Tester",
            "number": "123",
            "year": "9",
            "code": "asc",
        }
        response = self.client.post(reverse('api_app:payment', kwargs={"pk": self.order_id}),
                                    data=payment_data, content_type='application/json')
        self.assertEqual(response.status_code, 500)


class ProfileTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile = Profile.objects.create(user=self.user)
        self.client.force_login(self.user)

    def test_profile(self):
        profile_data = {
          "fullName": "New Name Tester",
          "email": "test@test.com",
          "phone": "88002000600",
          "avatar": {}
        }
        response_post = self.client.post(reverse("api_app:profile"), data=profile_data)
        self.assertEqual(response_post.status_code, 200)
        content = json.loads(response_post.content)
        self.assertEqual(content.get("fullName"), profile_data.get("fullName"))
        self.assertEqual(content.get("email"), profile_data.get("email"))
        self.assertEqual(content.get("phone"), profile_data.get("phone"))
        self.assertEqual(content.get("avatar"), None)

        response_get = self.client.get(reverse("api_app:profile"), data=profile_data)
        self.assertEqual(response_get.status_code, 200)
        content = json.loads(response_get.content)
        self.assertEqual(content.get("fullName"), profile_data.get("fullName"))
        self.assertEqual(content.get("email"), profile_data.get("email"))
        self.assertEqual(content.get("phone"), profile_data.get("phone"))
        self.assertEqual(content.get("avatar"), None)

    def test_set_password(self):
        data = {
            "currentPassword": "testpassword",
            "newPassword": "new_password",
        }
        response = self.client.post(reverse("api_app:password"), data=data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_password"))


class TagsTestCase(TestCase):
    def setUp(self) -> None:
        self.tag = Tag.objects.create(name="Test Tag")

    def test_tags(self):
        response = self.client.get(reverse("api_app:tags"))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content[0].get("name"), "Test Tag")


class ProductTestCase(TestCase):
    fixtures = ["fixtures/images_fixtures.json", "fixtures/categories_fixtures.json", "fixtures/catalog_fixture.json"]

    def test_products(self):
        response = self.client.get(reverse("api_app:product_details", kwargs={"pk": 1}))
        print("response", response.content)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        product = Product.objects.get(pk=1)

        self.assertEqual(content.get("category"), product.category.id)
        self.assertEqual(content.get("title"), product.title)
        self.assertEqual(float(content.get("price")), product.price)
        self.assertEqual(content.get("count"), product.count)
        self.assertEqual(content.get("description"), product.description)
        self.assertEqual(content.get("fullDescription"), product.fullDescription)
        self.assertEqual(content.get("freeDelivery"), product.freeDelivery)
        self.assertEqual(content.get("rating"), product.rating)
