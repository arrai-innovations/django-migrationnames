from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("users", "0001_initial"),
    ]

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    run_before = [
        ("app_one", "0001_squashed_initial"),
        ("app_two", "0001_squashed_initial"),
    ]
