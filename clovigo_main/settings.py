from pathlib import Path
import environ
import os

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env("SECRET_KEY")
SMS_API_KEY = env("SMS_API_KEY")
OTP_MAX_TRY = 3

DEBUG = True

ALLOWED_HOSTS = []
# ALLOWED_HOSTS = ["waybic.pro"]

AUTH_USER_MODEL = 'accounts.UserManagementModel'

INSTALLED_APPS = [
    'jazzmin',
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'cart',
    'products',
    'core',
    'orders',
    'drf_spectacular',
    # 'drf_spectacular_sidecar',
    'corsheaders',

]

MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'clovigo_main.urls'

CORS_ALLOW_CREDENTIALS = True


CORS_ALLOW_ALL_ORIGINS = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# import os

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Set global templates directory
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]


WSGI_APPLICATION = 'clovigo_main.wsgi.application'

DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.sqlite3',
     'NAME': BASE_DIR / 'db.sqlite3',}
#        {
#     'ENGINE': 'django.db.backends.mysql',
#     'NAME': 'clovigo',
#     'USER': 'root',
#     'PASSWORD': 'Jobin1624',
#     'HOST': 'localhost',
#     'PORT': '3306',
# }

}
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Kolkata' 
USE_I18N = True
USE_TZ = True

# STATIC_URL = 'static/'
STATIC_URL = '/clovigo/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}
CSRF_COOKIE_NAME = "csrftoken"  # Make sure the cookie name is set correctly
CSRF_COOKIE_HTTPONLY = False  # This should be False for AJAX requests


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'clovigo0@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'ftjd onfg sbix yxzp'  # Paste the 16-char app password here


SPECTACULAR_SETTINGS = {
    'TITLE': 'CloviGo',
    'DESCRIPTION': 'E-commerce and Food delivery app',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
# SPECTACULAR_SETTINGS = {
#     'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
#     'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
#     'REDOC_DIST': 'SIDECAR',
#     # OTHER SETTINGS
# }
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=70000),  # or 15, etc.
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7000),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}