# Generated by Django 4.2.3 on 2023-08-16 09:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0021_remove_category_subcategories_subcategory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subcategory',
            old_name='parent_category',
            new_name='category',
        ),
    ]
