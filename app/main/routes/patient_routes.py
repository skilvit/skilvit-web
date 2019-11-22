"""
Pour la connexion et les vues des patients
"""
import re
from flask import url_for
from flask_login import login_user, logout_user, login_required
from flask_babel import lazy_gettext, to_user_timezone, to_utc

import datetime
import time
from random import sample

from app.main import main
from app.main.routes_utils import *
from app.main.routes.main_routes import generer_pdf_site
from app.main.forms import NewFoodEntry, NewSleepEntry, NewSituationEntry, NewTakenPill, NewPhysicalActivity, \
    NewPatientForm, PatientConnexion
from app.data_manager import DateHeure
import app.database_manager as dbm
import app.sessions_manager as sm

from app.main.mail_manager import envoyer_mail_connexion_patient, envoyer_message_patient_vers_praticien


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
        return render_template("patient/connexion/connexion_patient_bs.html", connecte="connecte",
                               prenom=session["prenom"], nom=session["nom"])
    else:
        form = PatientConnexion()
        if form.validate_on_submit():
            patient = dbm.PatientDB.query.filter_by(email=form.email.data).first()
            if patient is None:
                flash("L'adresse email ou le mot de passe est incorrect.")
                return render_template("patient/connexion/connexion_patient_bs.html", connecte="pseudo_non_enrigistre",
                                       form=form)
            if not patient.verify_password(form.mdp_patient.data):
                flash("L'adresse email ou le mot de passe est incorrect.")
                return render_template("patient/connexion/connexion_patient_bs.html", connecte="mdp_incorrect",
                                       form=form)
            connecter_patient_login(patient)
            flash("Vous êtes bien connecté.")

            return redirect("/tcc/patient/index_patient")
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
        print("soumis", form.is_submitted())
        print(form.validate())
        print(form.errors)

        if form.validate_on_submit():
            already_exists = sm.Patients.check_if_patient_exists_by_email_address(form.email_address.data)

            if already_exists:
                print(already_exists)
                flash("Les informations données ne permettent pas de créer un compte patient.")
                return render_template("patient/connexion/nouveau_patient.html", form=form,
                                       message=lazy_gettext("Impossible de créer ce compte."))
            elif form.first_password.data != form.second_same_password.data:
                flash("Les mots de passe données ne sont pas identiques.")
                return render_template("patient/connexion/nouveau_patient.html", form=form,
                                       message=lazy_gettext("Les mots de passe ne sont pas identiques."))
            else:
                patient = sm.PatientSess.creer_nouveau(request.form, dbm.generate_password_hash(form.first_password.data))
                connecter_patient_login(patient)
                flash("Le compte a correctement été créé.")
                return render_template("patient/connexion/patient_enregistre.html", inscription_validee=True,
                                       mettre_message_succes=True)
            # if request.method == "POST":
            #     if not form.validate():
            #         for error in form.errors:

    form = NewPatientForm()
    return render_template("patient/connexion/nouveau_patient.html", form=form)


@main.route("/validation_inscription_patient/<string:link>", methods=["GET"])
def valider_inscription(link):
    patient = sm.Patients.retrieve_patient_by_validation_link(link)
    if patient is None:
        return redirect(url_for("/"))
    else:
        sm.Patients.validate_patient(patient)
        return redirect(url_for("/tcc/patient/connexion"))
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
                flash("Le praticien demandé n'existe pas.")
                return render_template("patient/praticiens/gestion_praticien.html", praticiens=praticiens,
                                       message_ajout_praticien="Le praticien demandé n'existe pas.")
            else:
                flash("La demande au praticien a correctement été envoyée.")
                return render_template("patient/praticiens/gestion_praticien.html", praticiens=praticiens,
                                       message_ajout_praticien="La demande au praticien "+res.prenom+" "+res.nom +
                                                               " a été envoyé.")
        else:
            flash("L'adresse courriel donné est invalide.")
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
            flash("Le message a correctement été envoyé.")
        else:
            flash("Erreur lors de l'envoi, veuillez réessayer plus tard.")
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
        flash("Le profil de praticien donné est inconnu.")
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
            flash("Le fichier JSON a bien été envoyé.")
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
            flash("Le fichier TXT a bien été envoyé.")
            return send_file(os.path.join(dbm.DIRECTORY_TXT, filename), mimetype="text/plain", as_attachment=True)

        elif "csv" in request.form and request.form["csv"]:
            patient = sm.PatientSess(session["pseudo_patient"])
            lignes = patient.to_csv()

            unique = "".join(sample("azertyuiopqsdfghjklmwxcvbn", 10)) + str(time.time()).split(".")[0]
            filename = unique + ".csv"
            with open(os.path.join(dbm.DIRECTORY_CSV, filename), "w") as f:
                for ligne in lignes:
                    f.write("\t".join(ligne)+"\n")
            flash("Le fichier CSV a bien été envoyé.")
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
                print("esle")
                flash("Il est impossible de générer le fichier PDF")
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


@main.route("/tcc/patient/anamnese", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def creer_et_voir_anamnese():
    if request.method == "POST":
        texte = request.form["texte-nouvelle-anamnese"]
        categorie = request.form["categorie"]
        patient = sm.PatientSess(session["pseudo_patient"])
        patient.ajouter_anamnese_patient(patient.patient_db.get_id(), texte, categorie)
        anamneses = patient.lire_anamnese_patient(patient.patient_db.get_id())
        return render_template("patient/profil/anamnese.html", patient=patient.patient_db,
                               categories=dbm.Anamnese.categories, anamneses=anamneses)
    else:
        patient = sm.PatientSess(session["pseudo_patient"])
        anamneses = patient.lire_anamnese_patient(patient.patient_db.get_id())
        print([(categorie, anamnese) for categorie, anamnese in anamneses.items()])
        return render_template("patient/profil/anamnese.html", patient=patient.patient_db,
                               categories=dbm.Anamnese.categories, anamneses=anamneses)


@main.route("/tcc/patient/anamnese/supprimer", methods=["POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def supprimer_anamnese():
    if request.method == "POST":
        id_anamnese = request.form["id_anamnese"]
        patient = sm.PatientSess(session["pseudo_patient"])
        patient.supprimer_anamnese_patient(patient.patient_db.get_id(), id_anamnese)
        return jsonify({"success": "ok"})
    return jsonify({"success": "ko"})


@main.route("/tcc/patient/anamnese/update", methods=["POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def mettre_a_jour_anamnese():
    if request.method == "POST":
        id_anamnese = request.form["id_anamnese"]
        nouveau_texte = request.form["texte"]
        patient = sm.PatientSess(session["pseudo_patient"])
        patient.mettre_a_jour_anamnese_patient(patient.patient_db.get_id(), id_anamnese, nouveau_texte)
        return jsonify({"success": "ok"})
    return jsonify({"success": "ko"})


# endregion


# region entrées
@main.route("/tcc/patient/menu_entrees", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_menu_entrees_patient():
    if "bouton_creer_nouvelle_entree" in request.form:
        return redirect(url_for("main.afficher_nouvelle_situation_patient"))
    elif "bouton_creer_fiche_repas" in request.form:
        return redirect(url_for("main.creation_nouvelle_fiche_alimentation"))
    elif "bouton_creer_evenement_sommeil" in request.form:
        return redirect(url_for("main.creation_nouvelle_fiche_sommeil"))
    elif "bouton_prise_medicament" in request.form:
        return redirect(url_for("main.creation_nouvelle_fiche_pm"))
    elif "bouton_creation_activite_physique" in request.form:
        return redirect(url_for("main.creation_nouvelle_fiche_activite_physique"))
    else:
        return render_template("patient/interface_patient.html")


@main.route("/tcc/patient/nouvelle_entree", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_nouvelle_situation_patient():
    form = NewSituationEntry()
    print("request.form", request.form)
    print("form.data", form.data)
    print("form.errors", form.errors)
    if request.method == "POST":
        if form.validate_on_submit():
            situation = dm.Situation()

            situation.from_view_to_data(request.form)
            patient = sm.PatientSess(session["pseudo_patient"])
            patient.enregistrer_entree_situation(situation)
            form.message_succes = "La situation est correctement enregistrée"
            maintenant = DateHeure()
            maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
            flash("La situation est bien enregistrée")
            return render_template("patient/entrees/entry_situation_form.html",
                                   message="La situation est bien enregistrée",
                                   form=form,
                                   maintenant=maintenant)

    maintenant = DateHeure()
    maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
    return render_template("patient/entrees/entry_situation_form.html", form=form, maintenant=maintenant)


@main.route("/tcc/patient/visualiser_entrees", methods=["GET"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_entrees_patient():
    patient = sm.PatientSess(session["pseudo_patient"])
    entrees = patient.to_json()
    print(entrees)
    return render_template("patient/entrees/visualisation_entrees.html", lignes=entrees)


@main.route("/tcc/patient/visualiser_entree/<int:indice>", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_entree_patient(indice):
    patient = sm.PatientSess(session["pseudo_patient"])
    entrees = patient.to_json()
    return render_template("patient/entrees/visualisation_entree.html", element=entrees[indice])


# @main.route("/tcc/patient/nouveau_repas", methods=["GET", "POST"])
# @validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
# def creation_nouvelle_fiche_alimentation():
#     if "POST" == request.method:
#         alim = dm.Alimentation()
#         alim.from_dictionary(request.form)
#         patient = sm.PatientSess(session["pseudo_patient"])
#         patient.enregistrer_entree_repas(alim)
#         return render_template("patient/entrees/nouvelle_entree_alimentation.html", message="La fiche est bien "
#                                                                                             "enregistrée.")
#     else:
#         return render_template("patient/entrees/nouvelle_entree_alimentation.html", message="")


@main.route("/tcc/patient/nouveau_repas", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def creation_nouvelle_fiche_alimentation():
    form = NewFoodEntry()
    print(request.form)
    print(form.data)
    print(form.validate())
    print(form.errors)
    if request.method == "POST":
        if form.validate_on_submit():

            alim = dm.Alimentation()
            alim.from_view_to_data(request.form)
            patient = sm.PatientSess(session["pseudo_patient"])
            patient.enregistrer_entree_repas(alim)
            maintenant = DateHeure()
            maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
            flash("La fiche repas a bien été enregistrée.")
            return render_template("patient/entrees/nouvelle_entree_alimentation.html",
                                   message="Vous avez bien rempli votre fiche alimentation", form=form,
                                   maintenant=maintenant)
            # return jsonify({"date_heure": request.form["date_heure"], "enrepas": request.form["enregistrement_repas"],
            #                 "nourriture": request.form["nourriture"], "repas": request.form["repas"]})

    maintenant = DateHeure()
    maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
    return render_template("patient/entrees/nouvelle_entree_alimentation.html",
                           form=form, maintenant=maintenant)


@main.route("/tcc/patient/nouvel_evenement_sommeil", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def creation_nouvelle_fiche_sommeil():
    form = NewSleepEntry()
    print(form.errors)
    print(form.validate())
    if request.method == "POST":
        if form.validate_on_submit():
            sommeil = dm.Sommeil()
            sommeil.from_new_webview(request.form)
            patient = sm.PatientSess(session["pseudo_patient"])
            print(session["pseudo_patient"])
            patient.enregistrer_entree_sommeil(sommeil)

            maintenant = DateHeure()
            maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))

            date_heure_evenement = DateHeure()
            date_heure_evenement.from_datetime(to_user_timezone(datetime.datetime.now()))
            flash("La fiche sommeil a bien été enregistrée.")
            return render_template("patient/entrees/nouvelle_entree_sommeil.html", message="", form=form,
                                   maintenant=maintenant, date_heure_evenement=date_heure_evenement)

    maintenant = DateHeure()
    maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
    date_heure_evenement = DateHeure()
    date_heure_evenement.from_datetime(to_user_timezone(datetime.datetime.now()))
    return render_template("patient/entrees/nouvelle_entree_sommeil.html", message="", maintenant=maintenant,
                           date_heure_evenement=date_heure_evenement, form=form)


@main.route("/tcc/patient/nouvelle_prise_medicament", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def creation_nouvelle_fiche_pm():
    form = NewTakenPill()
    if request.method == "POST":
        if form.validate_on_submit():
            pm = dm.PriseMedicament()
            pm.from_view_to_data(request.form)
            patient = sm.PatientSess(session["pseudo_patient"])
            patient.enregistrer_entree_prise_medicament(pm)
            maintenant = DateHeure()
            maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
            flash("La prise de médicament a bien été enregistrée.")
            return render_template("patient/entrees/nouvelle_entree_prise_medicament.html",
                                   message="La prise de médicament a bien été enregistrée", form=form,
                                   maintenant=maintenant)

    maintenant = DateHeure()
    maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
    return render_template("patient/entrees/nouvelle_entree_prise_medicament.html",
                           form=form, maintenant=maintenant)


@main.route("/tcc/patient/nouvelle_activite_physique", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def creation_nouvelle_fiche_activite_physique():
    form = NewPhysicalActivity()
    if request.method == "POST":
        if form.validate_on_submit():
            ap = dm.ActivitePhysique()
            ap.from_view_to_data(request.form)
            patient = sm.PatientSess(session["pseudo_patient"])
            patient.enregistrer_entree_activite_physique(ap)
            maintenant = DateHeure()
            maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
            flash("La fiche activité physique a bien été enregistrée.")
            return render_template("patient/entrees/nouvelle_activite_physique.html",
                                   message="L'activité physique est enregistrée", form=form, maintenant=maintenant)

    maintenant = DateHeure()
    maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
    return render_template("patient/entrees/nouvelle_activite_physique.html", form=form, maintenant=maintenant)
# endregion


@main.route("/tcc/patient/remplir_entree")
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def remplir_nouvelle_entree():
    pass


@main.route("/tcc/patient/page_inconnue")
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_patient_page_inconnue():
    return render_template("page_inconnue.html")


@main.route("/tcc/praticien/page_inconnue")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte"))
def afficher_praticien_page_inconnue():
    return render_template("page_inconnue.html")
