from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models


class Image(models.Model):
    src = models.CharField(max_length=255, blank=True, null=False, verbose_name=_("Path to img"))
    alt = models.CharField(max_length=255, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __str__(self):
        return "{alt} ({src_start}...{src_end})".format(alt=self.alt, src_start=self.src[:10], src_end=self.src[-20:])


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("title"))
    image = models.ForeignKey(Image, on_delete=models.PROTECT, null=False, verbose_name=_("Image"))

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.title


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='subcategories', verbose_name=_("Category"))
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    image = models.ForeignKey(Image, on_delete=models.PROTECT, blank=True, null=False, verbose_name=_("Image"))

    class Meta:
        verbose_name = _("Subcategory")
        verbose_name_plural = _("Subcategories")

    def __str__(self):
        return self.title


class Sale(models.Model):
    product = models.OneToOneField('Product', on_delete=models.CASCADE,
                                   verbose_name=_("Product"), related_name="product")
    oldPrice = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Old price"))
    salePrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Sale price"))
    dateFrom = models.DateField(verbose_name=_("Sale starts"))
    dateTo = models.DateField(verbose_name=_("Sale ends"))
    is_applied = models.BooleanField(default=False, verbose_name=_("Is applied"))
    is_active = models.BooleanField(default=False, verbose_name=_("Is active"))

    class Meta:
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")

    def __str__(self):
        msg = _("disabled")
        if self.is_active:
            msg = _("active")
        return _("sale on {title} ({msg})").format(title=self.product.title, msg=msg)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("Category"))
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    count = models.IntegerField(verbose_name=_("Count"))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Change date"))
    description = models.TextField(verbose_name=_("Description"))
    fullDescription = models.TextField(verbose_name=_("Full description"))
    freeDelivery = models.BooleanField(verbose_name=_("Free delivery"))
    images = models.ManyToManyField(Image, related_name='images', verbose_name=_("Images"), blank=True)
    tags = models.ManyToManyField('Tag', related_name='tags', verbose_name=_("Tags"), blank=True)
    reviews = models.ManyToManyField('Review', verbose_name=_("Reviews"), blank=True)
    specifications = models.ManyToManyField('Specification', verbose_name=_("Specifications"), blank=True)
    rating = models.FloatField(default=0, verbose_name=_("Rating"))
    is_limited = models.BooleanField(default=False, verbose_name=_("Is limited"))
    sold = models.IntegerField(default=0, verbose_name=_("Sold"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.title


class Review(models.Model):
    author = models.CharField(max_length=255, verbose_name=_("Author"))
    email = models.CharField(max_length=255, verbose_name=_("Email"))
    text = models.TextField(verbose_name=_("Review text"))
    rate = models.IntegerField(verbose_name=_("Rate"))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date"))

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")

    def __str__(self):
        return "{author} - {text}".format(author=self.author, text=self.text[:10])


class Specification(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    value = models.CharField(max_length=100, verbose_name=_("Value"))

    class Meta:
        verbose_name = _("Specification")
        verbose_name_plural = _("Specifications")

    def __str__(self):
        return "{name} - {value}".format(name=self.name, value=self.value)


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Product"))
    count = models.IntegerField(verbose_name=_("Count"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))

    class Meta:
        verbose_name = _("Order <-> Product")
        verbose_name_plural = _("Orders <-> Products")

    def __str__(self):
        return "{name} ({count})".format(name=self.product, count=self.count)


class Order(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    fullName = models.CharField(max_length=255, verbose_name=_("Full name"), null=True, blank=True)
    email = models.CharField(max_length=255, verbose_name=_("Email"), null=True, blank=True)
    phone = models.CharField(max_length=255, verbose_name=_("Phone"), null=True, blank=True)
    deliveryType = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Delivery type"))
    paymentType = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Payment type"))
    totalCost = models.DecimalField(max_digits=10, decimal_places=2,
                                    null=True, blank=True, verbose_name=_("Total cost"))
    status = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Status"))
    city = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("City"))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Address"))
    products = models.ManyToManyField(OrderProduct, verbose_name=_("Products"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return "#{id} {email} - {createdAt} ({status})".format(id=self.id, email=self.email,
                                                               createdAt=self.createdAt.date(), status=self.status)


class Basket(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("User"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Product"))
    count = models.IntegerField(verbose_name=_("Count"))

    class Meta:
        verbose_name = _("Basket")
        verbose_name_plural = _("Baskets")

    def __str__(self):
        return "#{id} {user}".format(id=self.id, user=self.user)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name


class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name=_("Order"))

    class Meta:
        verbose_name = _("Order's history")
        verbose_name_plural = _("Order's histories")
