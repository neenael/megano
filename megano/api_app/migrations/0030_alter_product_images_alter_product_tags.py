# Generated by Django 4.2.3 on 2023-08-17 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0029_remove_order_user_alter_product_reviews_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='images', to='api_app.image', verbose_name='Images'),
        ),
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tags', to='api_app.tag', verbose_name='Tags'),
        ),
    ]
