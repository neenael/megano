from django.contrib import admin
from .models import Profile
from django.utils.translation import gettext_lazy as _


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    fieldsets = [
        (_("Personal data"), {"fields": ("user", "fullName", "email", "phone", "avatar",)}),
    ]

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            self.readonly_fields = ("user", "fullName", "email", "phone", "avatar",)
            return self.readonly_fields
        return ()
