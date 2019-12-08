"""

"""

from flask_babel import lazy_gettext
from app.main.routes_utils import *
import app.sessions_manager as sm


__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


# region Gérer tâches
@main.route("/tcc/donner_taches", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def donner_taches():
    if request.method == "POST":
        # TODO enregistrer les tâches au patient voulu
        praticien = sm.PraticienSess(session["pseudo"])
        praticien.ajouter_tache_patient(request.form["patient_id"], request.form["tache"])
        flash(lazy_gettext("La tâche a bien été attribuée."))
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