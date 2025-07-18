# Generated by Django 5.2.3 on 2025-07-01 13:42

import django.db.models.deletion
import nanoid.generate
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=nanoid.generate,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                (
                    "description",
                    models.CharField(default="No course description", max_length=200),
                ),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("black", "Black"),
                            ("red", "Red"),
                            ("blue", "Blue"),
                            ("green", "Green"),
                            ("yellow", "Yellow"),
                        ],
                        default="red",
                        max_length=20,
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=nanoid.generate,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=150)),
                (
                    "description",
                    models.CharField(default="No course description", max_length=200),
                ),
                ("url", models.URLField()),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.course"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
