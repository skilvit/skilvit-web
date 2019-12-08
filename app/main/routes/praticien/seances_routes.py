"""

"""

from flask import url_for
from flask_babel import lazy_gettext

from app.main.routes_utils import *
from app.main.forms import FicheSeancePatientForm
import app.sessions_manager as sm
import datetime


__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


@main.route("/tcc/visualiser_patient/<int:index>/ajouter_fiche_seance", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def ajouter_fiche_seance(index):
    form = FicheSeancePatientForm()
    praticien = sm.PraticienSess(session["pseudo"])
    if form.validate_on_submit():
        date_heure = dm.DateHeure.from_select_datetime(request.form, "")
        praticien.ajouter_fiche_seance(index, form.contenu.data, date_heure)
        flash(lazy_gettext("La fiche consultation/séance a bien été ajoutée."))
        return redirect(url_for("main.afficher_fiches_seances", index=index))

    else:
        patient = praticien.acceder_patient(index)
        if patient:
            return render_template("praticien/ses_patients/creer_fiche_seance.html",
                                   aujourdhui=datetime.datetime.today(),
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
