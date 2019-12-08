"""
Routes et vues pour les praticiens
"""

from flask import url_for
from flask_login import login_user, logout_user, login_required
from flask_babel import lazy_gettext
from flask_mail import Message

from app import mail
from app.main import main
from app.main.routes_utils import *
from app.main.forms import PraticienConnexion, NewPraticienForm, FicheSeancePatientForm
import app.database_manager as dbm
import app.sessions_manager as sm
from app.main.mail_manager import envoyer_mail_attente_inscirption_praticien, \
    envoyer_mail_demande_inscription_praticien, envoyer_mail_connexion_praticien, envoyer_message_praticien_vers_patient
import datetime

__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


def connecter_praticien_login(user):
    if login_user(user):
        session["pseudo"] = user.email
        session["prenom"] = user.prenom
        session["nom"] = user.nom
        envoyer_mail_connexion_praticien(user)


# connexions
@main.route("/tcc/connexion_praticien", methods=["POST", "GET"])
def connecter_praticien():
    if "pseudo" in session:
        return render_template("praticien/connexion/connexion_praticien.html", connecte="connecte")
    else:
        form = PraticienConnexion()
        if form.validate_on_submit():
            praticien = dbm.PraticienDB.query.filter_by(email=form.pseudo_praticien.data).first()
            if praticien is None:
                flash(lazy_gettext("L'adresse email ou le mot de passe est incorrect."))
                return render_template("praticien/connexion/connexion_praticien.html", connecte="pseudo_non_enrigistre",
                                       form=form)
            elif not praticien.verify_password(form.mdp_praticien.data):
                flash(lazy_gettext("L'adresse email ou le mot de passe est incorrect."))
                return render_template("praticien/connexion/connexion_praticien.html", connecte="mdp_incorrect",
                                       form=form)
            connecter_praticien_login(praticien)
            flash(lazy_gettext("Vous êtes connecté."))
            return render_template("praticien/index_praticien.html", connecte="connecte", form=form)
        return render_template("praticien/connexion/connexion_praticien.html", connecte="pour_connexion", form=form)


@main.route("/tcc/pas_connecte_praticien")
def pas_connecte_praticien():
    return render_template("praticien/connexion/pas_connecte.html")


@main.route("/tcc/deconnexion_praticien")
def deconnecter_praticien():
    # session.pop("pseudo", None)
    # session.modified = True
    if logout_user():
        del session["pseudo"]
    return render_template("praticien/connexion/deconnexion_praticien.html")


@main.route("/tcc/nouveau_praticien", methods=["GET", "POST"])
def creer_nouveau_praticien():
    form = NewPraticienForm()
    if request.method == "POST":
        if form.validate_on_submit():
            already_exists = sm.Praticiens.check_if_praticien_exists_by_email_address(form.email_address.data) \
                             is not None
            if already_exists:
                flash(lazy_gettext("Les informations données ne permettent pas de créer un compte praticien."))
                return render_template("praticien/connexion/demande_nouveau_praticien.html", message="mauvaises_donnees",
                                       form=form)
            elif form.first_password.data != form.second_same_password.data:
                flash(lazy_gettext("Les mots de passe données ne sont pas identiques."))
                return render_template("praticien/connexion/demande_nouveau_praticien.html", message="mauvaises_donnees",
                                       form=form)
            else:
                # sm.PraticienSess.nouvelle_inscription_praticien(request.form)
                praticien = sm.PraticienSess.creer_nouveau(form,
                                                           dbm.generate_password_hash(form.first_password.data))
                if praticien:
                    envoyer_mail_attente_inscirption_praticien(praticien)
                    if request.form["first_password"] == request.form["second_same_password"]:
                        return render_template("praticien/connexion/demande_nouveau_praticien.html",
                                               message="attente_verification", form=form)
                    else:
                        flash(lazy_gettext("Les informations données ne permettent pas de créer un compte praticien."))
                        return render_template("praticien/connexion/demande_nouveau_praticien.html",
                                               message="mauvaises_donnees", form=form)
                else:
                    flash(lazy_gettext("Les informations données ne permettent pas de créer un compte praticien."))
                    return render_template("praticien/connexion/demande_nouveau_praticien.html",
                                           message="mauvaises_donnees", form=form)
    return render_template("praticien/connexion/demande_nouveau_praticien.html", message="inscription", form=form)


@main.route("/tcc/afficher_index_praticien")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def afficher_index_praticien():
    return render_template("praticien/index_praticien.html")


@main.route("/tcc/gestion_patients")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def gerer_ses_patients():
    praticien = sm.PraticienSess(session["pseudo"])
    ses_patients = praticien.acceder_patients()
    nouveaux_patients = praticien.acceder_nouveaux_patients()
    print(nouveaux_patients)
    return render_template("praticien/ses_patients/gestion_patients.html", patients=ses_patients,
                           nouveaux_patients=nouveaux_patients)


# Identité praticien
@main.route("/tcc/afficher_profil")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def afficher_profil():

    pra = sm.PraticienSess(session["pseudo"])
    return render_template("praticien/profil/mon_identite.html", praticien=pra.praticien_db)


@main.route("/tcc/ajax/praticien/ajouter_patient", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def ajouter_patient_ajax():
    if "POST" == request.method:
        praticien = sm.PraticienSess(session["pseudo"])
        email_patient = request.form["email"]
        patient = praticien.ajouter_patient(email_patient)

        if patient is None:
            return jsonify({"ajoute": False})
        else:
            return jsonify({"ajoute": True, "prenom": patient.prenom, "nom": patient.nom})
    else:
        return jsonify({"ajoute": False})


@main.route("/validation_inscription_praticien/<string:link>", methods=["GET"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def valider_praticien_inscription(link):
    praticien = sm.Praticiens.retrieve_praticien_by_validation_link(link)
    if praticien is None:
        return redirect(url_for("/"))
    else:
        sm.Praticiens.validate_praticien(praticien)
        return redirect(url_for("/tcc/connexion_praticien"))

# @main.route("valider_praticien", methods=["GET"])
# def valider_praticien():
#     envoyer_mail_demande_inscription_praticien()


@main.route("/tcc/contacter_patient/<int:index>", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def contacter_patient(index):
    if request.method == "POST":
        praticien = sm.PraticienSess(session["pseudo"])
        le_patient = praticien.acceder_patient(index)
        if le_patient:
            sujet = request.form["sujet-message"]
            corps = request.form["corps-message"]
            if envoyer_message_praticien_vers_patient(praticien, le_patient, sujet, corps):
                flash(lazy_gettext("Le message a correctement été envoyé."))
            else:
                flash(lazy_gettext("Erreur lors de l'envoi, veuillez réessayer plus tard."))
            return render_template("praticien/ses_patients/contacter_patient.html")
        else:
            return redirect(url_for("main.afficher_patient_inaccessible"))
    else:
        praticien = sm.PraticienSess(session["pseudo"])
        le_patient = praticien.acceder_patient(index)
        if le_patient:
            print(le_patient)
            return render_template("praticien/ses_patients/contacter_patient.html", patient=le_patient)
        else:
            return redirect(url_for("main.afficher_patient_inaccessible"))


@main.route("/tcc/supprimer_patient/<int:index>", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def suppression_patient(index):
    if request.method == "POST":
        # TODO remove patient
        pass

    else:
        praticien = sm.PraticienSess(session["pseudo"])
        ses_patients = praticien.acceder_patients()
        return render_template("praticien/ses_patients/suppression_patient.html")


@main.route("/tcc/visualiser_patient/<int:index>", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def visualiser_patient(index):
    if request.method == "POST":
        if "analyse_patient" in request.form:
            return redirect(url_for("main.visualiser_patient", index=index))
        elif "contacter_patient" in request.form:
            return redirect(url_for("main.contacter_patient", index=index))
        elif "suppression_patient" in request.form:
            return redirect(url_for("main.suppression_patient", index=index))
        elif "afficher_anamnese_patient" in request.form:
            return redirect(url_for('main.afficher_anamnese_patient', index=index))
    else:
        praticien = sm.PraticienSess(session["pseudo"])
        patient = praticien.acceder_patient(index)
        if patient is None:
            return redirect(url_for("main.afficher_patient_inaccessible"))
            pass
        entrees = praticien.voir_entrees_patient(patient.get_id())
        commentaires = praticien.voir_commentaires(patient.get_id())
        return render_template("praticien/ses_patients/visualisation_patient.html", patient=patient, entrees=entrees,
                               commentaires=commentaires)


@main.route("/tcc/supprimer_compte_praticien")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def supprimer_compte_praticien():
    praticien = sm.PraticienSess(session["pseudo"])
    praticien.supprimer_compte()
    return redirect("/tcc/deconnexion_praticien")


@main.route("/tcc/supprimer_compte_praticien")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def supprimer_definitivement_compte_praticien():
    # TODO Envoyer un email prévenant qu'on a tout supprimer
    # TODO tout supprimer
    # TODO déconnecter de la session
    return redirect(url_for("main.deconnecter_praticien"))


@main.route("/tcc/recuperer_mes_donnees_praticien")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def recuperer_mes_donnees_praticien():
    # TODO Envoyer un email prévenant qu'on a tout supprimer
    # TODO tout supprimer
    # TODO déconnecter de la session
    return redirect(url_for("main.afficher_profil"))


@main.route("/tcc/patient_inaccessible")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def afficher_patient_inaccessible():
    return render_template("praticien/ses_patients/patient_inaccessible.html")


@main.route("/tcc/visualiser_patient/<int:index>/anamnese")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def afficher_anamnese_patient(index):
    praticien = sm.PraticienSess(session["pseudo"])
    patient = praticien.acceder_patient(index)
    if patient is not None:
        anamneses = praticien.lire_anamnese_patient(patient.get_id())
        return render_template("praticien/ses_patients/afficher_anamnese.html", patient=patient,
                               categories=dbm.Anamnese.categories, anamneses=anamneses)
    return redirect(url_for("main.afficher_patient_inaccessible"))

