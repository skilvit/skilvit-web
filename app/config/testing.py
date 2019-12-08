import os


class Config:
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'top secret!'
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join('data-test.sqlite3')

    BABEL_DEFAULT_LOCALE = "fr"
    BABEL_DEFAULT_TIMEZONE = "Europe/Paris"
    BOOTSTRAP_USE_MINIFIED = True
    BOOTSTRAP_CDN_FORCE_SSL = True
    BOOTSTRAP_QUERYSTRING_REVVING = True
    # SERVER_NAME = "www.skilvit.fr"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_CHECK_DEFAULT = False

    MAIL_SERVER = ""
    # MAIL_PORT : default 25
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_DEBUG = True
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = ""
    # MAIL_MAX_EMAILS
    # MAIL_SUPPRESS_SEND : default app.testing
    # MAIL_ASCII_ATTACHMENTS : default False

    LANGUAGES = {
        "en": "English",
        "fr": "Français",
        "de": "Deutsch"
    }
