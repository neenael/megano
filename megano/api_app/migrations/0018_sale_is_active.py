# Generated by Django 4.2.3 on 2023-08-13 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0017_alter_sale_oldprice'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]