# Generated by Django 3.2.3 on 2024-01-26 15:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20240126_1522'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='coocking_time',
            new_name='cooking_time',
        ),
    ]