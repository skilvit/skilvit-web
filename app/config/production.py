
import os

__author__ = "Clément Besnier <skilvitapp@gmail.com>"


class Config:
    DEBUG = False
    SECRET_KEY = ''  # TODO define it
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '../data-prod.sqlite3')

    BABEL_DEFAULT_LOCALE = "fr"
    BABEL_DEFAULT_TIMEZONE = "Europe/Paris"
    BOOTSTRAP_USE_MINIFIED = True
    BOOTSTRAP_CDN_FORCE_SSL = True
    BOOTSTRAP_QUERYSTRING_REVVING = True
    SERVER_NAME = ""  # TODO define it
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_CHECK_DEFAULT = False

    MAIL_SERVER = ""  # TODO define it
    # MAIL_PORT : default 25
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_DEBUG = False
    MAIL_USERNAME = ""  # TODO define it
    MAIL_PASSWORD = ""  # TODO define it
    MAIL_DEFAULT_SENDER = ""  # TODO define it

    LANGUAGES = {
        "en": "English",
        "fr": "Français",
        "de": "Deutsch"
    }
