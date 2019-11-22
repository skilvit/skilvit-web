import datetime

from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField
import wtforms
from wtforms.validators import Length, DataRequired, Email, EqualTo
from wtforms.fields.html5 import EmailField

from app.utils import Sexe, EvenementSommeil


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(lazy_gettext("Le nom d'utilisateur est obligatoire")), Length(1, 16)])
    password = PasswordField('Password', validators=[
        DataRequired(lazy_gettext("Le mot de passe est obligatoire"))])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')


class NewPatientForm(FlaskForm):
    # nouveau_patient.html
    # "Fiche d'inscription - patient"
    titre = lazy_gettext("fiche_inscription_patient")
    # "Vous êtes bien inscrit"
    message_succes = lazy_gettext("bien_inscrit")
    # "Prénom"
    first_name = StringField(lazy_gettext("prenom"), validators=[DataRequired(
        lazy_gettext("Le prénom est obligatoire."))])
    # "Nom"
    family_name = StringField(lazy_gettext("nom"), validators=[DataRequired(
        lazy_gettext("Le nom de famille est obligatoire."))])
    # "Sexe"
    sex = wtforms.RadioField(lazy_gettext("sexe"), validators=[DataRequired(
        lazy_gettext("Il est impératif de spécifier le sexe."))], choices=[
        (Sexe.homme.name, Sexe.homme.name.capitalize()),
        (Sexe.femme.name, Sexe.femme.name.capitalize())
    ])
    # "Date de naissance"
    # birth_date = wtforms.DateField(lazy_gettext("date_naissance"), validators=[DataRequired()], format="%Y-%m-%d")
    # %d/%m/%Y
    # "Adresse email"
    email_address = EmailField(lazy_gettext("adresse_email"), validators=[
        DataRequired(lazy_gettext("L'adresse email est obligatoire.")),
        Email(lazy_gettext("Veuillez une adresse email correcte."))])
    # "Mot de passe"
    first_password = wtforms.PasswordField(lazy_gettext("mot_de_passe"), validators=[
        DataRequired(lazy_gettext("Il est impératif de donner le premier mot de passe.")),
        Length(min=6, message=lazy_gettext("Le mot de passe doit au moins contenir 6 caractères.")),
        EqualTo('second_same_password', message=lazy_gettext("Les mots de passe doivent correspondre."))])
    # "Le même mot de passe"
    second_same_password = wtforms.PasswordField(lazy_gettext("meme_mot_de_passe"), validators=[
        DataRequired(lazy_gettext("Il est impératif de remplir le second mot de passe.")),
        Length(min=6, message=lazy_gettext("Le mot de passe doit au moins contenir 6 caractères."))])
    # "Valider"
    submit = SubmitField(lazy_gettext("valider"))


class NewPraticienForm(FlaskForm):
    # "Fiche d'inscription - praticien"
    titre = lazy_gettext("fiche_inscription_praticien")
    # "Votre demande d'inscription est enregistré"
    message_succes = lazy_gettext("demande_inscription_enregistree")

    first_name = StringField(lazy_gettext("prenom"), validators=[
        DataRequired(lazy_gettext("Le prénom est obligatoire."))])
    family_name = StringField(lazy_gettext("nom"), validators=[
        DataRequired(lazy_gettext("Le nom de famille est obligatoire."))])

    job = StringField(lazy_gettext("profession"), validators=[
        DataRequired("La profession est obligatoire.")])

    email_address = EmailField(lazy_gettext("adresse_email"), validators=[
        DataRequired(lazy_gettext("L'adresse email est obligatoire.")),
        Email(lazy_gettext("Veuillez une adresse email correcte."))])

    # Numéro de téléphone fixe
    # numero_telephone_fixe = StringField(lazy_gettext("numero_telephone_fixe"))
    # "Numéro de téléphone mobile"
    phone_number = StringField(lazy_gettext("numero_telephone_mobile"))
    # "Rue"
    street = StringField(lazy_gettext("rue"))
    # "Code postale"
    post_code = StringField(lazy_gettext("code_postale"))
    # "Ville"
    city = StringField(lazy_gettext("ville"))

    # "Pays"
    country = StringField(lazy_gettext("pays"))

    # "Mot de passe"
    first_password = wtforms.PasswordField(lazy_gettext("mot_de_passe"),
                                           validators=[DataRequired(
                                               lazy_gettext("Il est impératif de donner le premier mot de passe.")),
                                               Length(min=8, message=lazy_gettext(
                                                   "Le mot de passe doit au moins contenir 8 caractères.")),
                                               EqualTo('second_same_password', message=lazy_gettext(
                                                   "Les mots de passe doivent correspondre."))])
    # "Le même mot de passe"
    second_same_password = wtforms.PasswordField(lazy_gettext("meme_mot_de_passe"),
                                                 validators=[
                                                     DataRequired(lazy_gettext(
                                                         "Il est impératif de remplir le second mot de passe.")),
                                                     Length(min=8, message=lazy_gettext(
                                                         "Le mot de passe doit au moins contenir 8 caractères."))])

    submit = SubmitField(lazy_gettext("valider"))


class PatientConnexion(FlaskForm):
    # connexion_patient.html
    titre = "Connexion au site en tant que patient"
    email = wtforms.StringField(lazy_gettext("Adresse email"),
                                validators=[DataRequired(lazy_gettext("L'adresse email est obligatoire.")),
                                            Email(lazy_gettext("Veuillez une adresse email correcte."))])
    mdp_patient = wtforms.PasswordField(lazy_gettext("Mot de passe"),
                                        validators=[DataRequired(
                                            lazy_gettext("Il est impératif de donner le premier mot de passe."))])
    tester_pseudo_mdp = wtforms.SubmitField(lazy_gettext("Connexion"))


class PraticienConnexion(FlaskForm):
    titre = "Connexion au site en tant que praticien"
    pseudo_praticien = StringField(lazy_gettext("Adresse email"),
                                   validators=[DataRequired(lazy_gettext("L'adresse email est obligatoire.")),
                                               Email(lazy_gettext("Veuillez une adresse email correcte."))])
    mdp_praticien = PasswordField(lazy_gettext("Mot de passe"),
                                  validators=[DataRequired(
                                      lazy_gettext("Il est impératif de donner le premier mot de passe."))])
    tester_pseudo_mdp = SubmitField(lazy_gettext("Connexion"))


class DataExportation(FlaskForm):
    # exportation_donnees.html
    pass


class AppDataExport(FlaskForm):
    # exportation_donnees_appli.html
    pass


class DataImport(FlaskForm):
    # importation_donnees.html
    pass


#
# class EntryMenu(Form):
#     # menu_entrees.html
#     menu_entrees = wtforms.SubmitField("Ajouter une nouvelle entrée")
#     gestion_praticien = wtforms.SubmitField("Gérer ses praticiens")
#     exportation_donnees = wtforms.SubmitField("Exporter les données")
#     importation_donnees = wtforms.SubmitField("Importer les données")
#     voir_profil = wtforms.SubmitField("Voir mon profil")
#     pass


class NewPhysicalActivity(FlaskForm):
    # nouvelle_activite_physique.html
    titre = lazy_gettext("Nouvelle fiche activité physique")
    message_succes = lazy_gettext("La fiche est bien enregistrée.")
    # date_heure = DateTimeLocalField("Date et heure", default=datetime.datetime.now())
    sport = wtforms.StringField(lazy_gettext("Sport"), validators=[DataRequired(
        lazy_gettext("Ce champ est obligatoire."))])
    duree = wtforms.IntegerField(lazy_gettext("Durée"), validators=[DataRequired(
        lazy_gettext("Ce champ est obligatoire."))])
    difficulte_ressentie = wtforms.StringField(lazy_gettext("Difficulté ressentie"), validators=[DataRequired(
        lazy_gettext("Ce champ est obligatoire."))])
    enregistrement_activite_physique = wtforms.SubmitField(lazy_gettext("Enregistrer"))
    pass


class NewFoodEntry(FlaskForm):
    # nouvelle_entree_alimentation.html
    # wtforms.fields.html5.DateTimeLocalField()
    titre = lazy_gettext("Nouvelle fiche repas")
    # date_heure = DateTimeLocalField("Date et heure", default=datetime.datetime.now(), format="%Y-%m-%dT%H:%M")
    repas = wtforms.RadioField("Repas", choices=[("petit_dejeuner", lazy_gettext("petit-déjeûner")),
                                                 ("dejeuner", lazy_gettext("déjeuner")),
                                                 ("gouter", lazy_gettext("goûter")), ("diner", lazy_gettext("dîner")),
                                                 ("grignotage", lazy_gettext("grignotage"))],
                               validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    nourriture = wtforms.TextAreaField(lazy_gettext("Contenu : "),
                                       validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    enregistrement_repas = wtforms.SubmitField(lazy_gettext("Enregistrer fiche repas"))


class NewAnamnesisEntry(FlaskForm):
    # nouvelle_entree_anamnese.html

    pass


class NewMenstrualEntry(FlaskForm):
    # nouvelle_entree_menstruelle.html
    titre = lazy_gettext("Nouvelle fiche sur les règles")
    # date_heure = DateTimeLocalField("Date et heure", default=datetime.datetime.now())
    commentaires = wtforms.StringField(lazy_gettext("Médicament : "), validators=[DataRequired(
        lazy_gettext("Ce champ est obligatoire."))])
    enregistrement_prise_medicament = wtforms.SubmitField(lazy_gettext("Enregistrer règles"))


class NewGlycemiaEntry(FlaskForm):
    # nouvelle_entree_glycemie.html
    titre = lazy_gettext("Nouvelle mesure de la glycémie")
    # date_heure = DateTimeLocalField("Date et heure", default=datetime.datetime.now())
    mesure = wtforms.StringField(lazy_gettext("Mesure : "), validators=[DataRequired(
        lazy_gettext("Ce champ est obligatoire."))])
    enregistrement_glycemie = wtforms.SubmitField(lazy_gettext("Enregistrer glycémie"))


class NewTakenPill(FlaskForm):
    # nouvelle_entree_prise_medicament.html
    titre = lazy_gettext("Nouvelle prise de médicament")
    # date_heure = DateTimeLocalField("Date et heure", default=datetime.datetime.now())
    medicament = wtforms.StringField(lazy_gettext("Médicament : "), validators=[DataRequired(
        lazy_gettext("Ce champ est obligatoire."))])
    dosage = wtforms.StringField(lazy_gettext("Dosage : "), validators=[DataRequired(
        lazy_gettext("Ce champ est obligatoire."))])
    enregistrement_prise_medicament = wtforms.SubmitField(lazy_gettext("Enregistrer prise médicament"))


class NewSleepEntry(FlaskForm):
    # nouvelle_entree_sommeil.html
    titre = lazy_gettext("Nouvelle fiche sommeil")
    # date_heure = DateTimeLocalField("Date et heure", default=datetime.datetime.now())
    evenement = wtforms.RadioField(lazy_gettext("evenement_sommeil"),
                                   validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))],
                                   choices=[
                                       (EvenementSommeil.coucher.name,
                                        lazy_gettext(EvenementSommeil.coucher.name.capitalize())),
                                       (EvenementSommeil.lever.name,
                                        lazy_gettext(EvenementSommeil.lever.name.capitalize())),
                                       (EvenementSommeil.reveil_nuit.name,
                                        lazy_gettext(EvenementSommeil.reveil_nuit.name.capitalize()))
                                   ])
    date_heure_evenement = wtforms.DateTimeField(lazy_gettext("Moment du sommeil"),
                                                 validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    commentaire = wtforms.TextAreaField(lazy_gettext("Commentaire"),
                                        validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    enregistrement_sommeil = wtforms.SubmitField(lazy_gettext("Enregistrer"))


class NewSituationEntry(FlaskForm):
    # nouvelle_situation.html
    titre = "Nouvelle situation"
    # date_heure = DateTimeLocalField("Date et heure", default=datetime.datetime.now())
    situation = wtforms.StringField(lazy_gettext("Donner la situation"),
                                    validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    emotions_sensations = wtforms.StringField(lazy_gettext("Quelles émotions et sensations ?"),
                                              validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    intensite = wtforms.IntegerField(lazy_gettext("Intensité : "),
                                     validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    pensees = wtforms.StringField(lazy_gettext("Pensée : "),
                                  validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    comportement = wtforms.StringField(lazy_gettext("Comportement : "),
                                       validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    enregistrement_entree = wtforms.SubmitField(lazy_gettext("Enregistrer"))


class NewSituationWithAlternative(NewSituationEntry):
    pass


class EntryVisualization(FlaskForm):
    # visualisation_entree.html
    pass


class EntriesVizualisation(FlaskForm):
    # visualisation_entrees.html
    pass


class PraticianAddConfirmation(FlaskForm):
    pass


class FicheSeancePatientForm(FlaskForm):
    titre = "Nouvelle fiche consultation/séance"
    date_heure = DateTimeField("Date et heure", default=datetime.datetime.now(),
                               validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    contenu = wtforms.TextAreaField(lazy_gettext("Texte"),
                                    validators=[DataRequired(lazy_gettext("Ce champ est obligatoire."))])
    enregistrement_fiche_seance = wtforms.SubmitField(lazy_gettext("Enregistrer"))
