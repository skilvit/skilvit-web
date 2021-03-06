import json

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import *

from app.config.development import Config

__author__ = ["Clément Besnier <admin@skilvit.fr>", ]

db = SQLAlchemy()


class JsonEncodedDict(db.TypeDecorator):
    @property
    def python_type(self):
        pass

    impl = db.String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


def row_to_dict(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns if c.name != "mdp_hash"}


class PatientDB(UserMixin, db.Model):
    __tablename__ = "patient"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prenom = db.Column(db.String(120), nullable=False)
    nom = db.Column(db.String(120), nullable=False)
    sexe = db.Column(db.Enum(Sexe), nullable=False)
    date_naissance = db.Column(db.DateTime, nullable=False)
    date_inscription = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(120), unique=True)
    # mdp = db.Column(db.String(80), unique=False, nullable=False)
    mdp_hash = db.Column(db.String(128), unique=False)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True, default=None)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)
    link_to_validate = db.Column(db.String(64), nullable=True, default="")

    # def __init__(self, prenom='', nom='', sexe=None, date_naissance=None, date_inscription=None, email='',
    # confirmed=False,
    #              confirmed_on=None):
    #     self.prenom = prenom
    #     self.nom = nom
    #     self.sexe = sexe
    #     self.date_naissance = date_naissance
    #     self.date_inscription = date_inscription
    #     self.email = email
    #     # mdp = db.Column(db.String(80), unique=False, nullable=False)
    #
    #     self.confirmed = confirmed
    #     self.confirmed_on = confirmed_on

    @staticmethod
    def row_to_dict(id_patient):
        row = PatientDB.query.filter_by(id=id_patient).first()
        row = row_to_dict(row)
        row.pop("confirmed")
        row.pop("confirmed_on")
        row.pop("is_admin")
        row.pop("link_to_validate")
        row["sexe"] = row["sexe"].get_pretty_form()
        row["date_naissance"] = row["date_naissance"].isoformat()
        row["date_inscription"] = row["date_inscription"].isoformat()
        return row

    def set_password(self, password):
        self.mdp_hash = generate_password_hash(password)

    def set_confirmed(self, confirmed):
        self.confirmed = confirmed

    def set_confirmed_on(self, confirmed_on):
        self.confirmed_on = confirmed_on

    def verify_password(self, password):
        return check_password_hash(self.mdp_hash, password)

    @staticmethod
    def register(email, password):
        patient = PatientDB(email=email)
        patient.set_password(password)
        db.session.add(patient)
        db.session.commit()
        return patient

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def __repr__(self):
        return '<Patient {0}>'.format(self.email)


class PraticienDB(UserMixin, db.Model):
    __tablename__ = "praticien"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prenom = db.Column(db.String(120), nullable=False)
    nom = db.Column(db.String(120), nullable=False)
    profession = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    numero_telephone = db.Column(db.String(120), nullable=False)
    date_inscription = db.Column(db.DateTime, nullable=False)
    # mdp = db.Column(db.String(80), unique=False, nullable=False)
    mdp_hash = db.Column(db.String(128), unique=False, nullable=False)
    rue = db.Column(db.String(120), nullable=True)
    code_postal = db.Column(db.String(120), nullable=True)
    ville = db.Column(db.String(120), nullable=True)
    pays = db.Column(db.String(50), nullable=True)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True, default=None)
    link_to_validate = db.Column(db.String(64), nullable=True, default="")
    patients = db.relationship("PatientDB", secondary="relation_pat_pra")

    # def __init__(self, prenom, nom, profession='', email='', numero_telephone='', rue='', code_postal='',
    #              ville='', pays='', confirmed=False, confirmed_on=None):
    #     self.prenom = prenom
    #     self.nom = nom
    #     self.profession = profession
    #     self.email = email
    #     self.numero_telephone = numero_telephone
    #     self.rue = rue
    #     self.code_postal = code_postal
    #     self.ville = ville
    #     self.pays = pays
    #
    #     self.confirmed = confirmed
    #     self.confirmed_on = confirmed_on

    def set_password(self, password):
        self.mdp_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.mdp_hash, password)

    def set_confirmed(self, confirmed):
        self.confirmed = confirmed

    def set_confirmed_on(self, confirmed_on):
        self.confirmed_on = confirmed_on

    @staticmethod
    def register(email, password):
        praticien = PraticienDB(email=email)
        praticien.set_password(password)
        db.session.add(praticien)
        db.session.commit()
        return praticien

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def __repr__(self):
        return '<Praticien {0}>'.format(self.email)

    @staticmethod
    def row_to_dict(id_praticien):
        row = PraticienDB.query.filter_by(id=id_praticien).first()
        row = row_to_dict(row)
        row["date_heure"] = row["date_heure"].isoformat()
        return row


class RelationPatientPraticienDB(db.Model):
    __tablename__ = "relation_pat_pra"
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, primary_key=True)
    patient = db.relationship(PatientDB)
    id_praticien = db.Column(db.Integer, db.ForeignKey('praticien.id'), nullable=False, primary_key=True)
    praticien = db.relationship(PraticienDB)
    date_heure_debut = db.Column(db.DateTime, nullable=False)
    actif = db.Column(db.Boolean, default=True)

    def get_id(self):
        return self.id


class DemandeConnexionPatientPraticienDB(db.Model):
    __tablename__ = "demande_connexion_patient_praticien"
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, primary_key=True)
    patient = db.relationship(PatientDB)
    id_praticien = db.Column(db.Integer, db.ForeignKey('praticien.id'), nullable=False, primary_key=True)
    praticien = db.relationship(PraticienDB)
    date_heure_demande = db.Column(db.DateTime, nullable=False, primary_key=True)
    repondu = db.Column(db.Boolean, default=False)

    def get_id(self):
        return self.id


class SituationDB(db.Model):
    __tablename__ = "situation"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)
    date_heure = db.Column(db.DateTime, nullable=False)
    intensite = db.Column(db.Integer)
    situation = db.Column(db.String(400), nullable=False)
    emotions_sensations = db.Column(db.String(200))
    comportement = db.Column(db.String(200))
    pensees = db.Column(db.String(300))
    taux_croyance = db.Column(db.String(10))
    pensee_alternative = db.Column(db.String(200))
    taux_croyance_actualise = db.Column(db.String(10))
    # info = db.Column(JsonEncodedDict, nullable=False)

    def get_id(self):
        return self.id

    @staticmethod
    def row_to_dict(id_situation):
        row = SituationDB.query.filter_by(id=id_situation).first()
        row = row_to_dict(row)
        row["date_heure"] = row["date_heure"].isoformat()
        return row


class PriseMedicamentDB(db.Model):
    __tablename__ = "prise_medicament"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)
    date_heure = db.Column(db.DateTime, nullable=False)
    medicament = db.Column(db.String(20), nullable=False)
    dosage = db.Column(db.String(20), nullable=False)

    def get_id(self):
        return self.id

    @staticmethod
    def row_to_dict(id_masse):
        row = PriseMedicamentDB.query.filter_by(id=id_masse).first()
        row = row_to_dict(row)
        row["date_heure"] = row["date_heure"].isoformat()
        return row


class AnalysePraticien(db.Model):
    __tablename__ = "analyse_praticien"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)
    id_praticien = db.Column(db.Integer, db.ForeignKey('praticien.id'))
    praticien = db.relationship(PraticienDB)
    date_heure = db.Column(db.DateTime, nullable=False)
    # contenu = db.Column(db.JSON
    contenu = db.Column(JsonEncodedDict)

    def get_id(self):
        return self.id

    @staticmethod
    def row_to_dict(id_masse):
        row = AnalysePraticien.query.filter_by(id=id_masse).first()
        row = row_to_dict(row)
        row["date_heure"] = row["date_heure"].isoformat()
        return row


class AlimentationDB(db.Model):
    __tablename__ = "alimentation"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)
    date_heure = db.Column(db.DateTime, nullable=False)
    repas = db.Column(db.String(20), nullable=False)
    nourriture = db.Column(db.String(200), nullable=False)
    info = db.Column(JsonEncodedDict, nullable=False)

    def get_id(self):
        return self.id

    @staticmethod
    def row_to_dict(is_alimentation):
        row = AlimentationDB.query.filter_by(id=is_alimentation).first()
        row = row_to_dict(row)
        row["date_heure"] = row["date_heure"].isoformat()
        return row


class ActivitePhysiqueDB(db.Model):
    __tablename__ = "activite_physique"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)
    date_heure = db.Column(db.DateTime, nullable=False)
    # info = db.Column(JsonEncodedDict, nullable=False)
    sport = db.Column(db.String(20))
    duree = db.Column(db.String(10))
    difficulte_ressentie = db.Column(db.String(100))

    def get_id(self):
        return self.id

    @staticmethod
    def row_to_dict(id_activite_physique):
        row = ActivitePhysiqueDB.query.filter_by(id=id_activite_physique).first()
        row = row_to_dict(row)
        row["date_heure"] = row["date_heure"].isoformat()
        return row


class SommeilDB(db.Model):
    __tablename__ = "sommeil"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)
    date_heure = db.Column(db.DateTime, nullable=False)
    evenement = db.Column(db.Enum(EvenementSommeil))
    date_heure_evenement = db.Column(db.DateTime)
    # date_heure_coucher = db.Column(db.DateTime)
    # date_heure_lever = db.Column(db.DateTime)
    # date_heure_reveil_nuit = db.Column(db.DateTime)
    commentaire = db.Column(db.String(100))

    def get_id(self):
        return self.id

    @staticmethod
    def row_to_dict(id_sommeil):
        row = SommeilDB.query.filter_by(id=id_sommeil).first()
        row = row_to_dict(row)
        row["date_heure"] = row["date_heure"].isoformat()
        row["date_heure_evenement"] = row["date_heure_evenement"].isoformat()
        return row


class MasseDB(db.Model):
    __tablename__ = "masse"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)
    date_heure = db.Column(db.DateTime, nullable=False)
    masse = db.Column(db.Integer, nullable=False)
    unite_masse = db.Column(db.Enum(UniteMasse), nullable=False, default=UniteMasse.kg)

    def get_id(self):
        return self.id

    @staticmethod
    def row_to_dict(id_masse):
        row = MasseDB.query.filter_by(id=id_masse).first()
        row = row_to_dict(row)
        row["unite_masse"] = row["unite_masse"].get_pretty_form()
        row["date_heure"] = row["date_heure"].isoformat()
        return row


class GlycemieDB(db.Model):
    __tablename__ = "glycemie"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)
    date_heure = db.Column(db.DateTime, nullable=False)
    glycemie = db.Column(db.Integer, nullable=False)

    def get_id(self):
        return self.id

    @staticmethod
    def row_to_dict(id_masse):
        row = GlycemieDB.query.filter_by(id=id_masse).first()
        row = row_to_dict(row)
        row["date_heure"] = row["date_heure"].isoformat()
        return row


class MessageEchangeDB(db.Model):
    __tablename__ = "message_echange"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)

    id_praticien = db.Column(db.Integer, db.ForeignKey('praticien.id'))
    praticien = db.relationship(PraticienDB)
    contenu = db.Column(db.String(1000), nullable=False)
    objet = db.Column(db.String(200), nullable=False)

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.email


class ProgrammeTherapeutiqueDB(db.Model):
    __tablename__ = "programme_therapeutique"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)

    def get_id(self):
        return self.id


class QuestionnaireDB(db.Model):
    __tablename__ = "questionnaire"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)

    id_praticien = db.Column(db.Integer, db.ForeignKey('praticien.id'))
    praticien = db.relationship(PraticienDB)
    date_creation = db.Column(db.DateTime, nullable=False)
    # contenu = db.Column(db.JSON, nullable=False)
    contenu = db.Column(JsonEncodedDict, nullable=False)

    def get_id(self):
        return self.id


class AccesQuestionnaireDB(db.Model):
    __tablename__ = "acces_questionnaire"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_questionnaire = db.Column(db.Integer, db.ForeignKey('questionnaire.id'))
    questionnaire = db.relationship(QuestionnaireDB)

    def get_id(self):
        return self.id


class SuiviPatient(db.Model):
    __tablename__ = "suivi_patient"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)

    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)

    id_praticien = db.Column(db.Integer, db.ForeignKey('praticien.id'))
    praticien = db.relationship(PraticienDB)

    # contenu = db.Column(db.JSON, nullable=False)
    contenu = db.Column(db.Text, nullable=False)

    date_heure = db.Column(db.DateTime, nullable=False)

    def get_id(self):
        return self.id


class TacheDB(db.Model):
    __tablename__ = "tache"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)

    id_praticien = db.Column(db.Integer, db.ForeignKey('praticien.id'))
    praticien = db.relationship(PraticienDB)
    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)
    date_creation = db.Column(db.DateTime, nullable=False)
    # contenu = db.Column(db.JSON, nullable=False)
    contenu = db.Column(JsonEncodedDict, nullable=False)

    def get_id(self):
        return self.id


class AnnotationEntree(db.Model):
    __tablename__ = "annotation_entree"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_entree = db.Column(db.Integer)
    tablename = db.Column(db.String(50))

    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)

    id_praticien = db.Column(db.Integer, db.ForeignKey('praticien.id'))
    praticien = db.relationship(PraticienDB)

    annotation = db.Column(db.String(500), default="", nullable=False)  # db.Text ?

    def get_id(self):
        return self.id


class Anamnese(db.Model):
    __tablename__ = "anamnese"
    __table_args__ = {'sqlite_autoincrement': True}
    categories = ["école", "travail et études", "amitié", "cercle familiale", "amour", "lieux de vie",
                  "événements marquants"]
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)

    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship(PatientDB)

    categorie = db.Column(db.String(30), nullable=False)

    contenu = db.Column(db.Text, default="", nullable=False)

    date_creation = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)

    def get_id(self):
        return self.id


def to_date(jour, mois, annee):
    jour_mois_annee = datetime.date(annee, mois, jour)
    return jour_mois_annee


PatientDB.situations = db.relationship("SituationDB", order_by=SituationDB.id, back_populates="patient",
                                       cascade="all, delete, delete-orphan")
PatientDB.sommeils = db.relationship("SommeilDB", order_by=SommeilDB.id, back_populates="patient",
                                     cascade="all, delete, delete-orphan")
PatientDB.masse = db.relationship("MasseDB", order_by=MasseDB.id, back_populates="patient",
                                  cascade="all, delete, delete-orphan")
PatientDB.anamneses = db.relationship("Anamnese", order_by=Anamnese.id, back_populates="patient",
                                      cascade="all, delete, delete-orphan")
PatientDB.prises_medicaments = db.relationship("PriseMedicamentDB", order_by=PriseMedicamentDB.id,
                                               back_populates="patient", cascade="all, delete, delete-orphan")
PatientDB.alimentations = db.relationship("AlimentationDB", order_by=AlimentationDB.id,
                                          back_populates="patient", cascade="all, delete, delete-orphan")
PatientDB.glycemies = db.relationship("GlycemieDB", order_by=GlycemieDB.id, back_populates="patient",
                                      cascade="all, delete, delete-orphan")
PatientDB.activites_physiques = db.relationship("ActivitePhysiqueDB", order_by=ActivitePhysiqueDB.id,
                                                back_populates="patient", cascade="all, delete, delete-orphan")
