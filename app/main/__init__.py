import flask
from flask import Blueprint
from flask.json import JSONEncoder
# from app.database_manager import JsonEncodedDict


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        JSONEncoder.default(self, obj)


Blueprint.json_encoder = CustomJSONEncoder

main = Blueprint('main', __name__)

from app.main.routes import main_routes
from app.main.routes.patient_routes import *
from app.main.routes.patient.anamnese_routes import *
from app.main.routes.patient.entries_routes import *
from app.main.routes.praticien_routes import *
from app.main.routes.questionnaire_routes import *
from app.main.routes_utils import *

