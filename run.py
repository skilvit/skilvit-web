#!/usr/bin/env python

import os
from app import create_app, db

__author__ = ["Clément Besnier <admin@skilvit.fr>", ]

if __name__ == '__main__':
    config_name = os.environ.get('FLASK_CONFIG') or 'development'
    # print(' * Loading configuration "{0}"'.format(config_name))
    app = create_app()
    with app.app_context():
        print(os.path.join(os.path.join(os.path.dirname(__file__), "app", "data-dev.sqlite3")))
        if not os.path.exists(os.path.join(os.path.join(os.path.dirname(__file__), "app", "data-dev.sqlite3"))):
            db.create_all()
    app.run(debug=True)
