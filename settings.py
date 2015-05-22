import os.path

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

INSTALLED_APPS = (
    'tests',
    'tests.polls',
)

SITE_ID = 1
SECRET_KEY = '+zzix-&k$afk-k0d0s7v01w0&15z#ne$71qf28#e$$c*@g742z'
ROOT_URLCONF = "tests.polls.urls"

DEBUG = True

STATIC_URL = '/static/'

DATABASES = {
    'default': {
        'TEST_NAME': os.path.join(os.path.dirname(__file__), 'test_database.db'),
        'TEST_ENGINE': 'django.db.backends.sqlite3',

        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'database.db'),
    },
}
