# Generated by Django 5.2.3 on 2025-07-01 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="document",
            name="name",
        ),
    ]
