from django.urls import path
from .views import (
    ProductViewSet, LimitedProductsViewSet, BannersViewSet,
    CategoriesViewSet, CatalogViewSet, login_view, logout_view,
    BasketViewSet, OrdersViewSet, PaymentViewSet, sign_up_view,
    ProfileViewSet, AvatarViewSet, SetPasswordViewSet,
    PopularProductsViewSet, TagsViewSet, ReviewViewSet, SalesViewSet
)

app_name = "api_app"

urlpatterns = [
    path("sign-in/", login_view, name="sign-in"),
    path("sign-up/", sign_up_view, name="sign-up"),
    path("sign-out/", logout_view, name="log-out"),

    path("categories/", CategoriesViewSet.as_view({"get": "list"}), name="categories"),
    path("catalog/", CatalogViewSet.as_view({'get': 'list'}), name="catalog"),
    path("products/popular/", PopularProductsViewSet.as_view({"get": "list"}), name="popular-products"),
    path("products/limited/", LimitedProductsViewSet.as_view({"get": "list"})),
    path("sales/", SalesViewSet.as_view({"get": "list"}), name="sales"),
    path("banners/", BannersViewSet.as_view({"get": "list"}), name="banners"),

    path("basket/", BasketViewSet.as_view({'get': 'list', 'delete': 'delete_product', 'post': 'add_product'}),
         name="basket"),

    path("orders/", OrdersViewSet.as_view({'get': 'list', 'post': 'create'}), name="orders"),
    path("order/<int:pk>/", OrdersViewSet.as_view({'post': 'add_order_info', 'get': 'retrieve'}), name="order"),

    path("payment/<int:pk>/", PaymentViewSet.as_view({'post': 'payment'}), name="payment"),

    path("profile/", ProfileViewSet.as_view({'get': 'retrieve', 'post': 'add_info'}), name="profile"),
    path("profile/password/", SetPasswordViewSet.as_view({'post': 'set_password'}), name="password"),
    path("profile/avatar/", AvatarViewSet.as_view({'post': 'set_avatar'}), name="avatar"),

    path("tags/", TagsViewSet.as_view({"get": "list"}), name="tags"),

    path("product/<int:pk>/", ProductViewSet.as_view({"get": "retrieve"}), name="product_details"),
    path("product/<int:pk>/reviews/", ReviewViewSet.as_view({"post": "add_review"}), name="reviews"),
]
