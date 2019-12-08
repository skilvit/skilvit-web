"""

"""

from app.main.routes_utils import *


from flask import url_for
from flask_babel import lazy_gettext, to_user_timezone, to_utc

import datetime

from app.main import main
from app.main.forms import NewFoodEntry, NewSleepEntry, NewSituationEntry, NewTakenPill, NewPhysicalActivity, \
    NewWeightEntry
from app.data_manager import DateHeure
import app.database_manager as dbm
import app.sessions_manager as sm


__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


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
    elif "bouton_creation_masse" in request.form:
        return redirect(url_for("main.creation_nouvelle_fiche_poids"))
    else:
        return render_template("patient/interface_patient.html")


@main.route("/tcc/patient/nouvelle_entree", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_nouvelle_situation_patient():
    form = NewSituationEntry()
    # print("request.form", request.form)
    # print("form.data", form.data)
    # print("form.errors", form.errors)
    if request.method == "POST":
        if form.validate_on_submit():
            situation = dm.Situation()

            situation.from_view_to_data(request.form)
            patient = sm.PatientSess(session["pseudo_patient"])
            patient.enregistrer_entree_situation(situation)
            form.message_succes = lazy_gettext("La situation est correctement enregistrée")
            maintenant = DateHeure()
            maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
            flash(lazy_gettext("La situation est bien enregistrée"))
            return redirect(url_for("main.afficher_menu_entrees_patient"))
        else:
            flash(lazy_gettext("Il y a au moins une erreur dans le formulaire"))
            return redirect(url_for("main.afficher_nouvelle_situation_patient"))

    maintenant = DateHeure()
    maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
    return render_template("patient/entrees/entry_situation_form.html", form=form, maintenant=maintenant)


@main.route("/tcc/patient/visualiser_entrees", methods=["GET"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_entrees_patient():
    patient = sm.PatientSess(session["pseudo_patient"])
    entrees = patient.entries_to_json()
    print(entrees)
    return render_template("patient/entrees/visualisation_entrees.html", lignes=entrees)


@main.route("/tcc/patient/visualiser_entree/<int:indice>", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def afficher_entree_patient(indice):
    patient = sm.PatientSess(session["pseudo_patient"])
    entrees = patient.entries_to_json()
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
    if request.method == "POST":
        if form.validate_on_submit():

            alim = dm.Alimentation()
            alim.from_view_to_data(request.form)
            patient = sm.PatientSess(session["pseudo_patient"])
            patient.enregistrer_entree_repas(alim)
            maintenant = DateHeure()
            maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
            flash("La fiche repas a bien été enregistrée.")
            return redirect(url_for("main.afficher_menu_entrees_patient"))
            # return jsonify({"date_heure": request.form["date_heure"], "enrepas": request.form["enregistrement_repas"],
            #                 "nourriture": request.form["nourriture"], "repas": request.form["repas"]})
        else:
            flash(lazy_gettext("Il y a au moins une erreur dans le formulaire"))
            return redirect(url_for("main.creation_nouvelle_fiche_alimentation"))

    maintenant = DateHeure()
    maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
    return render_template("patient/entrees/nouvelle_entree_alimentation.html",
                           form=form, maintenant=maintenant)


@main.route("/tcc/patient/nouvel_evenement_sommeil", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def creation_nouvelle_fiche_sommeil():
    form = NewSleepEntry()
    if request.method == "POST":
        if form.validate_on_submit():
            sommeil = dm.Sommeil()
            sommeil.from_new_webview(request.form)
            patient = sm.PatientSess(session["pseudo_patient"])
            patient.enregistrer_entree_sommeil(sommeil)

            maintenant = DateHeure()
            maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))

            date_heure_evenement = DateHeure()
            date_heure_evenement.from_datetime(to_user_timezone(datetime.datetime.now()))
            flash(lazy_gettext("La fiche sommeil a bien été enregistrée."))
            return redirect(url_for("main.afficher_menu_entrees_patient"))
        else:
            flash(lazy_gettext("Il y a au moins une erreur dans le formulaire"))
            return redirect(url_for("main.creation_nouvelle_fiche_sommeil"))

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
            flash(lazy_gettext("La prise de médicament a bien été enregistrée."))
            return redirect(url_for("main.afficher_menu_entrees_patient"))
        else:
            flash(lazy_gettext("Il y a au moins une erreur dans le formulaire"))
            return redirect(url_for("main.creation_nouvelle_fiche_pm"))

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
            flash(lazy_gettext("La fiche activité physique a bien été enregistrée."))
            return redirect(url_for("main.afficher_menu_entrees_patient"))
        else:
            flash(lazy_gettext("Il y a au moins une erreur dans le formulaire"))
            return redirect(url_for("main.creation_nouvelle_fiche_activite_physique"))

    maintenant = DateHeure()
    maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
    return render_template("patient/entrees/nouvelle_activite_physique.html", form=form, maintenant=maintenant)


@main.route("/tcc/patient/nouveau_poids", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def creation_nouvelle_fiche_poids():
    form = NewWeightEntry()
    if request.method == "POST":
        if form.validate_on_submit():
            masse = dm.Masse()
            masse.from_view_to_data(request.form)
            patient = sm.PatientSess(session["pseudo_patient"])
            patient.enregistrer_poids(masse)
            maintenant = DateHeure()
            maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
            flash(lazy_gettext("La fiche poids a bien été enregistrée."))
            return redirect(url_for("main.afficher_menu_entrees_patient"))
        else:
            flash(lazy_gettext("Il y a au moins une erreur dans le formulaire "+
                               "\n".join(["\t\n".join(form.errors[kind]) for kind in form.errors])))
            return redirect(url_for("main.creation_nouvelle_fiche_poids"))

    maintenant = DateHeure()
    maintenant.from_datetime(to_user_timezone(datetime.datetime.now()))
    return render_template("patient/entrees/nouvelle_entree_poids.html", form=form, maintenant=maintenant)
# endregion


@main.route("/tcc/patient/remplir_entree")
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def remplir_nouvelle_entree():
    pass
