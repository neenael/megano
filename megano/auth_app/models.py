from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from api_app.models import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    fullName = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Full name"))
    email = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Phone"))
    avatar = models.OneToOneField(Image, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Avatar"))

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.user.username
