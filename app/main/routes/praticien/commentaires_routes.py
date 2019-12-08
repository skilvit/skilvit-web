"""

"""

from app.main.routes_utils import *
import app.sessions_manager as sm


__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


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

        praticien = sm.PraticienSess(session["pseudo"])
        commentaires_voulus = praticien.charger_commentaire_sur_entree_patient(patient_id, tabl_ids)
        if commentaires_voulus:
            l = []
            for commentaire in commentaires_voulus:
                l.append({'name': commentaire.tablename+':'+str(commentaire.id_entree),
                          'id_commentaire': commentaire.get_id(),
                          'texte': commentaire.annotation})
            return jsonify(l)
        else:
            return jsonify({"success": "false"})


@main.route("/tcc/supprimer_commentaire_entree", methods=["POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def supprimer_commentaire_entree():
    if request.method == "POST":
        formulaire = request.form
        patient_id = int(formulaire["patient_id"])
        comment_id = int(formulaire["comment_id"])

        praticien = sm.PraticienSess(session["pseudo"])
        praticien.supprimer_commentaires_sur_entree_patient(patient_id, comment_id)
        return jsonify({"success": "true"})
