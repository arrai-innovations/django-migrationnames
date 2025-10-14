from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("app_one", "0001_initial"),
    ]

    run_before = [
        ("app_two", "0001_squashed_initial"),
    ]
