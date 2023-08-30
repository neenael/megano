# Generated by Django 4.2.3 on 2023-08-16 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0023_remove_category_is_child_alter_subcategory_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(related_name='images', to='api_app.image'),
        ),
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='api_app.tag'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]