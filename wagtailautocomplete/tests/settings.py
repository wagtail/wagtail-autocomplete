SECRET_KEY = "NOTSECRET"

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "wagtailautocomplete.sqlite",
    }
}

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "wagtail",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.admin",
    "wagtail.sites",
    "wagtail.users",
    "taggit",
    "wagtailautocomplete",
    "wagtailautocomplete.tests.testapp",
    "wagtail.snippets",
)

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "wagtailautocomplete.tests.testapp.urls"

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

WAGTAIL_SITE_NAME = "wagtail-autocomplete test site"

WAGTAILADMIN_BASE_URL = "http://localhost:8020"
