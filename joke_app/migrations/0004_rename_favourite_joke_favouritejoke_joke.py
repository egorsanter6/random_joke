# Generated by Django 5.1.4 on 2024-12-29 17:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('joke_app', '0003_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='favouritejoke',
            old_name='favourite_joke',
            new_name='joke',
        ),
    ]