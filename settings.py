from pathlib import Path

# --------------------------------------------------
# BASE DIRECTORY
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# --------------------------------------------------
# SECURITY SETTINGS
# --------------------------------------------------
SECRET_KEY = 'django-insecure-final-year-dynamic-pricing-project'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost','192.168.101.29']

# --------------------------------------------------
# INSTALLED APPS
# --------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom App
    'pricing',
    'django_crontab',
]


# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# --------------------------------------------------
# URL CONFIGURATION
# --------------------------------------------------
ROOT_URLCONF = 'dynamic_pricing.urls'


# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # global templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# --------------------------------------------------
# WSGI
# --------------------------------------------------
WSGI_APPLICATION = 'dynamic_pricing.wsgi.application'


# --------------------------------------------------
# DATABASE (SQLite – Recommended for BTech)
# --------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --------------------------------------------------
# LANGUAGE & TIME ZONE
# --------------------------------------------------
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True
USE_TZ = True


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# --------------------------------------------------
# DEFAULT PRIMARY KEY
# --------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --------------------------------------------------
# EMAIL CONFIGURATION (SAFE CONSOLE MODE)
# --------------------------------------------------
# Emails will be printed in terminal instead of being sent
# 100% acceptable for college demo and testing

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'pricingm12@gmail.com'
EMAIL_HOST_PASSWORD = 'xsmh zajc kkad hjzz'

# --------------------------------------------------
# SITE BASE URL (USED FOR APPROVAL LINKS)
# --------------------------------------------------
SITE_BASE_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# LOGIN REDIRECTS
# --------------------------------------------------
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SITE_BASE_URL = "http://127.0.0.1:8000"

CRONJOBS = [
    ('*/5 * * * *', 'pricing.cron.scheduled_price_check'),
]


# --------------------------------------------------
# UIPATH ORCHESTRATOR CONFIGURATION
# --------------------------------------------------
# Replace these with your UiPath Cloud Orchestrator credentials.
# Sign up at https://cloud.uipath.com to obtain these values.

UIPATH_TENANT_URL = "https://cloud.uipath.com/eStore/DefaultTenant/orchestrator_"
UIPATH_CLIENT_ID = "a2290d3b-e01a-44f9-aef2-14b644c9f50d"
UIPATH_CLIENT_SECRET = "QAv_9I1NhB%VKp%3Oo*tXbTkJZufDAQ_6v?hCppct6sH*0oF^Yz1?CF$KvbYr!vD"
UIPATH_SCOPE = "OR.Jobs OR.Execution OR.Assets OR.Robots"
UIPATH_FOLDER_ID = 7602106  # Your Orchestrator Modern Folder ID

# Tavily AI Configuration
TAVILY_API_KEY = "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"
