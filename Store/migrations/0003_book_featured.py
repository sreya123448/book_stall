# Generated by Django 5.2.1 on 2025-05-23 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0002_category_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]
