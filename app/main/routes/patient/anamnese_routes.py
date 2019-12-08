"""

"""

from app.main.routes_utils import *

from app.main import main
import app.database_manager as dbm
import app.sessions_manager as sm
import app.validation as validation

__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


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
        # print([(categorie, anamnese) for categorie, anamnese in anamneses.items()])
        return render_template("patient/profil/anamnese.html", patient=patient.patient_db,
                               categories=dbm.Anamnese.categories, anamneses=anamneses)


@main.route("/tcc/patient/anamnese/supprimer", methods=["POST"])
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def supprimer_anamnese():
    if request.method == "POST":
        id_anamnese = request.form["id_anamnese"]
        if not validation.validate_id(id_anamnese):
            return jsonify({"success": "ko"})
        patient = sm.PatientSess(session["pseudo_patient"])
        res = patient.supprimer_anamnese_patient(patient.patient_db.get_id(), id_anamnese)
        if res:
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
