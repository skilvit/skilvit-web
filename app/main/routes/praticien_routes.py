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

__author__ = "Clément Besnier <skilvitapp@gmail.com>"


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
                flash("L'adresse email ou le mot de passe est incorrect.")
                return render_template("praticien/connexion/connexion_praticien.html", connecte="pseudo_non_enrigistre",
                                       form=form)
            elif not praticien.verify_password(form.mdp_praticien.data):
                flash("L'adresse email ou le mot de passe est incorrect.")
                return render_template("praticien/connexion/connexion_praticien.html", connecte="mdp_incorrect",
                                       form=form)
            connecter_praticien_login(praticien)
            flash("Vous êtes connecté.")
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
    print(form.data)
    if request.method == "POST":
        if form.validate_on_submit():
            already_exists = dbm.db.session.query(email=form.email_address.data).first() is not None
            if already_exists:
                print("Il existe ")
                flash("Les informations données ne permettent pas de créer un compte praticien.")
                return render_template("praticien/connexion/demande_nouveau_praticien.html", message="mauvaises_donnees",
                                       form=form)
            elif form.first_password.data != form.second_same_password.data:
                flash("Les mots de passe données ne sont pas identiques.")
                return render_template("praticien/connexion/demande_nouveau_praticien.html", message="mauvaises_donnees",
                                       form=form)
            else:
                # sm.PraticienSess.nouvelle_inscription_praticien(request.form)
                praticien = sm.PraticienSess.creer_nouveau(request.form,
                                                           dbm.generate_password_hash(form.first_password.data))
                valide = True
                if valide:
                    envoyer_mail_attente_inscirption_praticien(praticien)
                    if request.form["first_password"] == request.form["second_same_password"]:
                        return render_template("praticien/connexion/demande_nouveau_praticien.html",
                                               message="attente_verification", form=form)
                    else:
                        flash("Les informations données ne permettent pas de créer un compte praticien.")
                        return render_template("praticien/connexion/demande_nouveau_praticien.html",
                                               message="mauvaises_donnees", form=form)
                else:
                    flash("Les informations données ne permettent pas de créer un compte praticien.")
                    return render_template("praticien/connexion/demande_nouveau_praticien.html",
                                           message="mauvaises_donnees", form=form)
    return render_template("praticien/connexion/demande_nouveau_praticien.html", message="inscription", form=form)
    # if request.method == "POST":
    #     TODO vérification des données
    #     écriture de la demande d'ajout
    # sm.PraticienSess.nouvelle_inscription_praticien(request.form)


# region Gérer tâches
@main.route("/tcc/donner_taches", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def donner_taches():
    if request.method == "POST":
        # TODO enregistrer les tâches au patient voulu
        praticien = sm.PraticienSess(session["pseudo"])
        praticien.ajouter_tache_patient(request.form["patient_id"], request.form["tache"])
        flash("La tâche a bien été attribuée.")
        return render_template("praticien/taches/donner_taches.html", message="valide")
    else:
        praticien = sm.PraticienSess(session["pseudo"])
        ses_patients = praticien.acceder_patients()
        return render_template("praticien/taches/donner_taches.html", patients=ses_patients)

# @main.route("/tcc/ajax/valider_taches", methods=["GET", "POST"])
# def valider_taches():
#     if request.method == "POST":


@main.route("/tcc/taches_donnees")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def voir_taches_donnees():
    # TODO récupérer les tâches données
    praticien = sm.PraticienSess(session["pseudo"])
    ses_patients = praticien.acceder_patients()
    taches = dm.get_taches(ses_patients)
    return render_template("praticien/taches/taches_donnees.html",
                           patients={patient.get_id(): patient for patient in ses_patients}, taches=taches)
# endregion


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
                flash("Le message a correctement été envoyé.")
            else:
                flash("Erreur lors de l'envoi, veuillez réessayer plus tard.")
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


@main.route("/tcc/visualiser_patient/<int:index>/ajouter_fiche_seance", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def ajouter_fiche_seance(index):
    form = FicheSeancePatientForm()

    praticien = sm.PraticienSess(session["pseudo"])
    if form.validate_on_submit():
        print("date et heure : ", form.date_heure.data)
        date_heure = dm.DateHeure.from_select_datetime(request.form, "")
        praticien.ajouter_fiche_seance(index, form.contenu.data, date_heure)
        flash("La fiche consultation/séance a bien été ajoutée.")
        return redirect(url_for("main.afficher_fiches_seances", index=index))

    else:
        patient = praticien.acceder_patient(index)
        if patient:
            return render_template("praticien/ses_patients/creer_fiche_seance.html", aujourdhui=datetime.datetime.today(),
                               patient=patient, form=form)
        else:
            return redirect(url_for("main.afficher_patient_inaccessible"))


@main.route("/tcc/visualiser_patient/<int:index>/afficher_fiches_seances", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def afficher_fiches_seances(index):
    praticien = sm.PraticienSess(session["pseudo"])
    patient = praticien.acceder_patient(index)
    fiches_seances = praticien.afficher_fiches_seances(index)
    if patient is None:
        return redirect(url_for("main.afficher_patient_inaccessible"))
    return render_template("praticien/ses_patients/fiches_seances.html", fiches_seances=fiches_seances, patient=patient)


@main.route("/tcc/supprimer_fiche_seance", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def supprimer_fiche_seance():
    if request.method == "POST":
        formulaire = request.form
        patient_id = int(formulaire["patient_id"])
        fiche_id = int(formulaire["fiche_id"])

        praticien = sm.PraticienSess(session["pseudo"])
        praticien.supprimer_fiche_seance(patient_id, fiche_id)
        return jsonify({"success": "true"})


@main.route("/tcc/modifier_fiche_seance", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def modifier_fiche_seance():
    if request.method == "POST":
        formulaire = request.form
        patient_id = int(formulaire["patient_id"])
        fiche_id = int(formulaire["fiche_id"])
        texte = str(formulaire["texte"])

        praticien = sm.PraticienSess(session["pseudo"])
        praticien.modifier_fiche_seance(patient_id, fiche_id, texte)
        return jsonify({"success": "true"})


@main.route("/tcc/visualiser_patient/<int:index>", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def visualiser_patient(index):
    if request.method == "POST":
        print(request.form)
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


@main.route("/tcc/ajouter_commentaire", methods=["POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def ajouter_commentaire_entree():
    if request.method == "POST":
        formulaire = request.form
        texte = formulaire["texte"]
        name = formulaire["name"]
        patient_id = formulaire["patient_id"]
        tablename, entry_id = name.split(":")
        praticien = sm.PraticienSess(session["pseudo"])
        commentaire_id = praticien.ajouter_commentaire_sur_entree_patient(entry_id, tablename, texte, patient_id)
        if commentaire_id:
            return jsonify({"success": "true", "commentaire_id": commentaire_id})
        else:
            return jsonify({"success": "false"})


@main.route("/tcc/charger_commentaires_entrees", methods=["POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def charger_commentaires_entrees():
    if request.method == "POST":
        formulaire = request.form
        # print(formulaire)
        patient_id = int(formulaire["patient_id"])
        tabl_ids = [(i.split(':')[0], int(i.split(':')[1])) for i in json.loads(formulaire["entrees_ids"])]

        print(tabl_ids)
        praticien = sm.PraticienSess(session["pseudo"])
        commentaires_voulus = praticien.charger_commentaire_sur_entree_patient(patient_id, tabl_ids)
        print(commentaires_voulus)
        if commentaires_voulus:
            l = []
            for commentaire in commentaires_voulus:
                l.append({'name': commentaire.tablename+':'+str(commentaire.id_entree),
                          'id_commentaire': commentaire.get_id(),
                          'texte': commentaire.annotation})
            print(l)
            return jsonify(l)
        else:
            return jsonify({"success": "false"})


@main.route("/tcc/supprimer_commentaire_entree", methods=["POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def supprimer_commentaire_entree():
    if request.method == "POST":
        formulaire = request.form
        # print(formulaire)
        patient_id = int(formulaire["patient_id"])
        comment_id = int(formulaire["comment_id"])

        praticien = sm.PraticienSess(session["pseudo"])
        praticien.supprimer_commentaires_sur_entree_patient(patient_id, comment_id)
        return jsonify({"success": "true"})


@main.route("/tcc/supprimer_compte_praticien")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def supprimer_compte_praticien():
    # vers page de confirmation
    return render_template("praticien/profil/supprimer.html")


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

