# Generated by Django 4.2.3 on 2023-08-13 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0019_rename_is_active_sale_is_applied'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
