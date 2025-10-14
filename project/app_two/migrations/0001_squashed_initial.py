from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("app_two", "0001_initial"),
    ]

    dependencies = [
    ]
