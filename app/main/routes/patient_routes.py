"""
Pour la connexion et les vues des patients
"""

import re
from flask import url_for
from flask_login import login_user, logout_user, login_required
from flask_babel import lazy_gettext

import datetime
import time
from random import sample

from app.main import main
from app.main.routes_utils import *
from app.main.routes.main_routes import generer_pdf_site
from app.main.forms import NewPatientForm, PatientConnexion
import app.database_manager as dbm
import app.sessions_manager as sm

from app.main.mail_manager import envoyer_mail_connexion_patient, envoyer_mail_demande_inscription_patient, \
    envoyer_message_patient_vers_praticien


__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


# region connexion
def connecter_patient_login(user):
    if login_user(user):
        session["pseudo_patient"] = user.email
        session["prenom"] = user.prenom
        session["nom"] = user.nom
        envoyer_mail_connexion_patient(user)


@main.route("/tcc/patient/connexion", methods=["POST", "GET"])
def connecter_patient():
    if "pseudo_patient" in session:
        return redirect(url_for("main.afficher_menu_principal_patient"))
    else:
        form = PatientConnexion()
        if form.validate_on_submit():
            patient = dbm.PatientDB.query.filter_by(email=form.email.data).first()
            if patient is None:
                flash(lazy_gettext("L'adresse email ou le mot de passe est incorrect."))
                return render_template("patient/connexion/connexion_patient_bs.html", connecte="pseudo_non_enrigistre",
                                       form=form)
            if not patient.verify_password(form.mdp_patient.data):
                flash(lazy_gettext("L'adresse email ou le mot de passe est incorrect."))
                return render_template("patient/connexion/connexion_patient_bs.html", connecte="mdp_incorrect",
                                       form=form)
            connecter_patient_login(patient)
            flash(lazy_gettext("Vous êtes bien connecté."))
            return redirect(url_for("main.afficher_menu_principal_patient"))

        return render_template('patient/connexion/connexion_patient_bs.html', connecte="pour_connexion", form=form,
                               mettre_message_succes=False, now=datetime.datetime.utcnow())


@main.route("/tcc/pas_connecte_patient")
def pas_connecte_patient():
    return render_template("patient/connexion/pas_connecte_patient.html")


# @login_required
@main.route("/tcc/patient/deconnexion")
def deconnecter_patient():
    if logout_user():
        if"pseudo_patient" in session:
            del session["pseudo_patient"]
        if "prenom" in session:
            del session["prenom"]
        if "nom" in session:
            del session["nom"]
    # session.pop("pseudo_patient", None)
    # session.modified = True
    return render_template("patient/connexion/deconnexion_patient.html")


@main.route("/tcc/patient/nouveau_patient", methods=["GET", "POST"])
def creer_nouveau_patient():
    if request.method == "POST":
        form = NewPatientForm()
        if form.validate_on_submit():
            already_exists = sm.Patients.check_if_patient_exists_by_email_address(form.email_address.data) is not None
            if already_exists:
                flash(lazy_gettext("Les informations données ne permettent pas de créer un compte patient."))
                return render_template("patient/connexion/nouveau_patient.html", form=form,
                                       message=lazy_gettext("Impossible de créer ce compte."))
            elif form.first_password.data != form.second_same_password.data:
                flash(lazy_gettext("Les mots de passe données ne sont pas identiques."))
                return render_template("patient/connexion/nouveau_patient.html", form=form,
                                       message=lazy_gettext("Les mots de passe ne sont pas identiques."))
            else:
                patient = sm.PatientSess.creer_nouveau(form, dbm.generate_password_hash(form.first_password.data))
                if patient:
                    connecter_patient_login(patient)
                    flash(lazy_gettext("Le compte a correctement été créé."))
                    return redirect(url_for("main.afficher_menu_principal_patient"))
                    # return render_template("patient/connexion/patient_enregistre.html", inscription_validee=True,
                    #                        mettre_message_succes=True)
                else:
                    flash(lazy_gettext("Les données reçues sont invalides"))
                    render_template("patient/connexion/nouveau_patient.html", form=form)
        else:
            flash(lazy_gettext("Les données reçues sont invalides : \n"
                               "\n".join(["\t\n".join(form.errors[kind]) for kind in form.errors])))
            return render_template("patient/connexion/nouveau_patient.html", form=form, errors=form.errors)

    form = NewPatientForm()
    return render_template("patient/connexion/nouveau_patient.html", form=form)


@main.route("/validation_inscription_patient/<string:link>", methods=["GET"])
def valider_inscription(link):
    patient = sm.Patients.retrieve_patient_by_validation_link(link)
    if patient is None:
        return redirect(url_for("main.connecter_patient"))
    else:
        sm.Patients.validate_patient(patient)
        return redirect(url_for("main.afficher_menu_principal_patient"))
# endregion


# region menu
@main.route("/tcc/patient/index_patient", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_menu_principal_patient():
    if request.method == "POST":
        if "menu_entrees" in request.form:
            return redirect(url_for("main.afficher_menu_entrees_patient"))
        elif "bouton_visualiser_entrees" in request.form:
            return redirect(url_for("main.afficher_entrees_patient"))
        elif "gestion_praticien"in request.form:
            return redirect(url_for("main.gerer_praticiens"))
        elif "exportation_donnees" in request.form:
            return redirect(url_for("main.exporter_donnees"))
        elif "importation_donnees" in request.form:
            return redirect(url_for("main.importer_donnees"))
        elif "voir_profil" in request.form:
            return redirect("/tcc/patient/voir_profil")
    else:
        return render_template("patient/entrees/menu_entrees.html")
# endregion


# region gestion des praticiens
@main.route("/tcc/patient/gerer_praticien", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
@login_required
def gerer_praticiens():
    patient = sm.PatientSess(session["pseudo_patient"])
    praticiens = patient.acceder_praticiens()
    if "POST" == request.method:
        if re.match(dbm.EMAIL_PATTERN, request.form["ajout_email_pratcien"]) is not None:
            res = patient.definir_praticien(request.form["ajout_email_pratcien"])
            if res is None:
                flash(lazy_gettext("Le praticien demandé n'existe pas."))
                return render_template("patient/praticiens/gestion_praticien.html", praticiens=praticiens,
                                       message_ajout_praticien="Le praticien demandé n'existe pas.")
            else:
                flash(lazy_gettext("La demande au praticien a correctement été envoyée."))
                return redirect("main.afficher_menu_principal_patient")
        else:
            flash(lazy_gettext("L'adresse courriel donné est invalide."))
            return render_template("patient/praticiens/gestion_praticien.html", praticiens=praticiens,
                                   message_ajout_praticien="Vous avez donné une adresse email invalide.")
    else:
        return render_template("patient/praticiens/gestion_praticien.html", praticiens=praticiens)


@main.route("/tcc/patient/contacter_praticien/<int:numero_praticien>", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def contacter_son_praticien(numero_praticien):
    if request.method == "POST":
        patient = sm.PatientSess(session["pseudo_patient"])
        praticien = patient.obtenir_praticien(numero_praticien)
        sujet = request.form["sujet-message"]
        corps = request.form["corps-message"]
        if envoyer_message_patient_vers_praticien(praticien, patient, sujet, corps):
            flash(lazy_gettext("Le message a correctement été envoyé."))
            return redirect(url_for("main.contacter_son_praticien"))
        else:
            flash(lazy_gettext("Erreur lors de l'envoi, veuillez réessayer plus tard."))
            return render_template("patient/praticiens/contacter_praticien.html", praticien=praticien)
    else:
        patient = sm.PatientSess(session["pseudo_patient"])
        praticien = patient.obtenir_praticien(numero_praticien)
        return render_template("patient/praticiens/contacter_praticien.html", praticien=praticien)


@main.route("/tcc/patient/profil_praticien/<int:numero_praticien>")
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_profil_praticien(numero_praticien):
    patient = sm.PatientSess(session["pseudo_patient"])
    praticiens = patient.acceder_praticiens()
    print(praticiens)
    if 0 < numero_praticien <= len(praticiens):
        return render_template("patient/praticiens/profil_praticien.html", praticien=praticiens[numero_praticien-1])
    else:
        flash(lazy_gettext("Le profil de praticien donné est inconnu."))
        return redirect(url_for("main.afficher_patient_page_inconnue"))
# endregion


# region application
@main.route("/tcc/patient/export_pdf/<string:filename>")
def envoyer_rapport_patient_appli(filename):
    return send_file(os.path.join(dbm.DIRECTORY_TMP_LATEX, filename), "application/pdf")


# appli
@main.route("/tcc/appli/notice")
def afficher_notice_appli():
    return render_template("appli/notice.html")
# endregion


# region importation et exportation
@main.route("/tcc/ajax/importation_donnees", methods=['GET', 'POST'])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def importer_ses_donnees():
    if "POST" == request.method:
        # TODO enregistrer le fichier JSON
        pass


@main.route("/tcc/patient/exportation_donnees", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def exporter_donnees():
    # TODO exporter les données en format PDF avec un long récapitulatif !!!!
    # TODO exporter les données en format JSON avec tout de répertorié
    if request.method == "POST":
        print(request.form)

        if "json" in request.form and request.form["json"]:
            patient = sm.PatientSess(session["pseudo_patient"])
            entrees = patient.to_json()
            unique = "".join(sample("azertyuiopqsdfghjklmwxcvbn", 10)) + str(time.time()).split(".")[0]
            filename = unique + ".json"
            with open(os.path.join(dbm.DIRECTORY_JSON, filename), "w") as f:
                json.dump(entrees, f)
            flash(lazy_gettext("Le fichier JSON a bien été envoyé."))
            return send_file(os.path.join(dbm.DIRECTORY_JSON, filename), mimetype="application/json",
                             as_attachment=True)

        elif "txt" in request.form and request.form["txt"]:
            patient = sm.PatientSess(session["pseudo_patient"])
            lignes = patient.to_txt()

            unique = "".join(sample("azertyuiopqsdfghjklmwxcvbn", 10)) + str(time.time()).split(".")[0]
            filename = unique + ".txt"
            if not os.path.exists(dbm.DIRECTORY_TXT):
                os.mkdir(dbm.DIRECTORY_TXT)
            with open(os.path.join(dbm.DIRECTORY_TXT, filename), "w") as f:
                for ligne in lignes:
                    f.write(ligne + "\n")
            flash(lazy_gettext("Le fichier TXT a bien été envoyé."))
            return send_file(os.path.join(dbm.DIRECTORY_TXT, filename), mimetype="text/plain", as_attachment=True)

        elif "csv" in request.form and request.form["csv"]:
            patient = sm.PatientSess(session["pseudo_patient"])
            lignes = patient.to_csv()

            unique = "".join(sample("azertyuiopqsdfghjklmwxcvbn", 10)) + str(time.time()).split(".")[0]
            filename = unique + ".csv"
            with open(os.path.join(dbm.DIRECTORY_CSV, filename), "w") as f:
                for ligne in lignes:
                    f.write("\t".join(ligne)+"\n")
            flash(lazy_gettext("Le fichier CSV a bien été envoyé."))
            return send_file(os.path.join(dbm.DIRECTORY_CSV, filename), mimetype="text/csv", as_attachment=True)

        if "pdf" in request.form and request.form["pdf"]:
            patient = sm.PatientSess(session["pseudo_patient"])
            entrees = patient.to_json()
            unique = "".join(sample("azertyuiopqsdfghjklmwxcvbn", 10)) + str(time.time()).split(".")[0]
            ret = generer_pdf_site(unique, entrees)
            if ret == 0:
                filename = unique + ".pdf"
                return send_file(os.path.join(dbm.DIRECTORY_TMP_LATEX, filename), "application/pdf", as_attachment=True)
            else:
                flash(lazy_gettext("Il est impossible de générer le fichier PDF"))
                # return render_template("patient/entrees/exportation_donnees.html")

        return render_template("patient/entrees/exportation_donnees.html", message="envoyé")
    else:
        return render_template("patient/entrees/exportation_donnees.html")


@main.route("/tcc/patient/importation_donnees", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def importer_donnees():
    # TODO lire le fichier json récupéré par POST et extraire tout le contenu et l'enregistrer dans la base de données
    return render_template("patient/entrees/importation_donnees.html")
# endregion


# region profil patient
@main.route("/tcc/patient/voir_profil")
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def voir_profil():
    patient = sm.PatientSess(session["pseudo_patient"])
    return render_template("patient/profil/mon_identite.html", patient=patient.patient_db)


@main.route("/tcc/patient/supprimer_compte")  # API
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connect_patient"))
def supprimer_profil_patient():
    patient = sm.PatientSess(session["pseudo_patient"])
    patient.supprimer_compte()
    return redirect(url_for("main.deconnecter_patient"))

# endregion



@main.route("/tcc/patient/page_inconnue")
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_patient_page_inconnue():
    return render_template("page_inconnue.html")


@main.route("/tcc/praticien/page_inconnue")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte"))
def afficher_praticien_page_inconnue():
    return render_template("page_inconnue.html")
