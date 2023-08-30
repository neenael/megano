from rest_framework import serializers
from auth_app.models import Profile
from .models import (Image, Category, Product, Review,
                     Specification, OrderProduct, Order, Basket,
                     Tag, OrderHistory, Subcategory)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['src', 'alt']


class SubcategorySerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = Subcategory
        fields = ['id', 'title', 'image']


class CategorySerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'subcategories']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']


class ProductShortSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    reviews = serializers.SerializerMethodField()

    def get_reviews(self, obj):
        return obj.reviews.count()

    class Meta:
        model = Product
        fields = ['id', 'category', 'title', 'price', 'count', 'date', 'description',
                  'freeDelivery', 'images', 'tags', 'reviews', 'rating']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['name', 'value']


class ProductFullSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    specifications = SpecificationSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'title', 'price', 'count', 'date', 'description', 'fullDescription', 'freeDelivery',
                  'images', 'tags', 'reviews', 'specifications', 'rating']


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer()

    class Meta:
        model = OrderProduct
        fields = ['product', 'count', 'price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        count_in_basket = instance.count
        print("count_in_basket", count_in_basket)
        product_value = representation['product']
        product_value['count'] = count_in_basket
        products = representation['product']
        return products


class OrderProductListSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer()

    class Meta:
        model = OrderProduct
        fields = ['product']


class OrderListSerializer(serializers.ModelSerializer):
    products = ProductShortSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'createdAt', 'fullName', 'email', 'phone', 'deliveryType', 'paymentType', 'totalCost', 'status',
                  'city', 'address', 'products']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product_value = representation['product']
        return product_value


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'createdAt', 'fullName', 'email', 'phone', 'deliveryType', 'paymentType', 'totalCost', 'status',
                  'city', 'address', 'products']


class BasketCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = ["id", "product", ]


class BasketSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer()

    class Meta:
        model = Basket
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        count_in_basket = instance.count
        product_value = representation['product']
        product_value['count'] = count_in_basket
        return product_value


class ProfileSerializer(serializers.ModelSerializer):
    avatar = ImageSerializer()

    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']


class OrderHistorySerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = OrderHistory
        fields = ['order']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product_value = representation['order']
        return product_value


class SaleItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    salePrice = serializers.DecimalField(max_digits=10, decimal_places=2)
    dateFrom = serializers.DateField()
    dateTo = serializers.DateField()
    title = serializers.CharField()
    images = ImageSerializer(many=True)
