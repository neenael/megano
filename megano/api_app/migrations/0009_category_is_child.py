# Generated by Django 4.2.3 on 2023-07-24 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0008_alter_product_reviews_alter_product_specifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_child',
            field=models.BooleanField(default=False),
        ),
    ]
