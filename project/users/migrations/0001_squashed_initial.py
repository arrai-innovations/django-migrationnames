from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("users", "0001_initial"),
    ]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    run_before = [
        ("app_thirteen", "0001_squashed_initial"),
        ("app_eighteen", "0001_squashed_initial"),
    ]
