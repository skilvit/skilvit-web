import os
from app import create_app_test, db

__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


if __name__ == '__main__':
    # config_name = os.environ.get('FLASK_CONFIG') or 'development'
    # print(' * Loading configuration "{0}"'.format(config_name))

    if os.path.exists('data-test.sqlite3'):
        os.remove('data-test.sqlite3')
    app = create_app_test()
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    app.run(debug=True)
