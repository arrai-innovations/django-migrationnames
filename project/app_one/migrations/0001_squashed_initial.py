from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("app_one", "0001_initial"),
    ]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    run_before = [
        ("app_two", "0001_squashed_initial"),
    ]
