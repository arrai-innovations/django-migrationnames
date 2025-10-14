from pathlib import Path

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = ROOT_DIR / "project"

DEBUG = True
TIME_ZONE = "America/Edmonton"
LANGUAGE_CODE = "en-us"
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "project_database",
    }
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "project.management_command",
    "project.app_one.apps.AppOneConfig",
    "project.app_four.apps.AppSevenConfig",
    # "project.app_six.apps.AppSixConfig",
    "project.app_nine.apps.AppNineConfig",
    "project.app_eleven.apps.AppElevenConfig",
    "project.app_twelve.apps.AppTwelveConfig",
    "project.app_thirteen.apps.AppThirteenConfig",
    "project.app_fifteen.apps.AppFifteenConfig",
    "project.app_sixteen.apps.AppSixteenConfig",
    "project.app_seventeen.apps.AppSeventeenConfig",
    "project.app_eighteen.apps.AppEighteenConfig",
    "project.users.apps.UsersConfig",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
AUTH_USER_MODEL = "users.User"

SECRET_KEY = "the-secret-key"
