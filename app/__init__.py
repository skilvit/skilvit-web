import os
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_babel import Babel, lazy_gettext, gettext
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from wtforms.validators import Length, DataRequired, ValidationError
from wtforms import StringField, PasswordField, BooleanField, SubmitField
import wtforms
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin, AdminIndexView, expose, helpers
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

from app.database_manager import db, PatientDB, PraticienDB, RelationPatientPraticienDB, \
    DemandeConnexionPatientPraticienDB, SituationDB, TacheDB, QuestionnaireDB, AnnotationEntree, SuiviPatient
from app.config.development import Config


bootstrap = Bootstrap()
babel = Babel()

lm = LoginManager()
# lm.login_view = 'main.index'

csrf = CSRFProtect()
mail = Mail()
migrate = Migrate()
moment = Moment()


class SkilvitAdminModelView(ModelView):
    page_size = 50  # the number of entries to display on the list view
    column_exclude_list = ['password', ]

    def is_accessible(self):
        # print(current_user.is_active)
        # print(current_user.is_authenticated)
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if hasattr(current_user, "is_admin"):
            if current_user.is_admin:
                return True
        return False


class AdminLoginForm(wtforms.form.Form):
    email = StringField(validators=[wtforms.validators.required()])
    password = PasswordField(validators=[wtforms.validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(PatientDB).filter_by(email=self.email.data).first()


class RegistrationForm(wtforms.form.Form):
    login = wtforms.fields.StringField(validators=[wtforms.validators.required()])
    email = wtforms.fields.StringField()
    password = wtforms.fields.PasswordField(validators=[wtforms.validators.required()])

    def validate_login(self, field):
        if db.session.query(PatientDB).filter_by(email=self.login.data).count() > 0:
            raise wtforms.validators.ValidationError('Duplicate username')


class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = AdminLoginForm(request.form)
        print('login viw')
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)
            print('validat')

        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        print(form)
        self._template_args['form'] = form
        # link = '<p>Don't have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        # self._template_args['link'] = link
        print('login ntr')
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


def create_app():
    """Create an application instance."""
    app = Flask(__name__)

    # import configuration
    # cfg = os.path.join(os.getcwd(), 'app', 'config', config_name + '.py')
    app.config.from_object(Config)
    # app.config.from_pyfile(cfg)
    app.secret_key = Config.SECRET_KEY

    # initialize extensions
    bootstrap.init_app(app)
    db.init_app(app)

    # login manager for admin
    lm.init_app(app)

    babel.init_app(app)
    # print(babel.list_translations())
    # print(babel.default_locale)
    # print(babel.default_timezone)
    # print(babel.translation_directories)
    csrf.init_app(app)
    mail.init_app(app)

    # admin page
    admin = Admin(app, "Administration", base_template='my_master.html', index_view=MyAdminIndexView(),
                  template_mode="bootstrap3")
    admin.add_view(SkilvitAdminModelView(PatientDB, db.session))
    admin.add_view(SkilvitAdminModelView(PraticienDB, db.session))
    admin.add_view(SkilvitAdminModelView(RelationPatientPraticienDB, db.session))
    admin.add_view(SkilvitAdminModelView(DemandeConnexionPatientPraticienDB, db.session))
    admin.add_view(SkilvitAdminModelView(SituationDB, db.session))
    admin.add_view(SkilvitAdminModelView(TacheDB, db.session))
    admin.add_view(SkilvitAdminModelView(QuestionnaireDB, db.session))
    admin.add_view(SkilvitAdminModelView(AnnotationEntree, db.session))
    admin.add_view(SkilvitAdminModelView(SuiviPatient, db.session))

    # migration
    migrate.init_app(app, db)
    moment.init_app(app)

    @lm.user_loader
    def load_user(user_id):
        return PatientDB.query.get(int(user_id))

    # import blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    print("application lancée")
    return app
