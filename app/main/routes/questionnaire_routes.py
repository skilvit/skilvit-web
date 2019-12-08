
import re
from random import shuffle

from app.main import main
from app.main.routes_utils import *
import app.sessions_manager as sm
from app.utils import *


__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


def serie_questionnaire_en_json(data):
    d = {"titre": data["titre"]}
    p_q = re.compile(r"^question_(?P<n_question>[0-9]*?)$")
    for key in data:
        print(key)
        m = re.search(p_q, key)
        if m is not None:
            n_question = m.group("n_question")
            print(n_question)
            d[n_question] = {"texte": data[key], "reponses": []}
            for j in data:

                p_qr = re.compile(r"^question_"+n_question+r"_reponse_(?P<n_reponse>[0-9]*?)$")
                m = re.search(p_qr, j)
                if m is not None:
                    n_reponse = m.group("n_reponse")

                    d[n_question]["reponses"].append({"reponse": data["question_"+n_question+"_reponse_"+n_reponse],
                                                      "poids": data["question_"+n_question+"_poids_"+n_reponse]})
    return d


# --------------------QUESTIONAIRE---------------------------
@main.route("/tcc/accueil_questionnaire", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def afficher_accueil_questionnaire():
    if "creation_questionnaire" in request.form:
        return redirect("/tcc/creation_questionnaire")
    elif "consultation_questionnaire" in request.form:
        return redirect("/tcc/consulter_questionnaire")
    elif "modification_questionnaire" in request.form:
        return redirect("/tcc/modification_questionnaire")
    elif "choisir_questionnaire" in request.form:
        return redirect("/tcc/choisir_questionnaire")
    else:
        return render_template("praticien/questionnaire/accueil_questionnaire.html")


@main.route("/tcc/creation_questionnaire")
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def afficher_creation_questionnaire():
    # TODO enregistrer le nouveau questionnaire
    return render_template("praticien/creation_questionnaire.html")


@main.route("/tcc/ajax/verifier_enregistrer_questionnaire", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", "")
def verifier_enregistrer_questionnaire():
    print(request.form)

    if len(request.form):

        # data = {elem.split("=")[0]: elem.split("=")[1] for elem in request.form["data"].split("&")}
        # request.form = data
        print("on a reçu la validation")
        print(request.form)
        resultat = serie_questionnaire_en_json(request.form)
        # dico = [elem for elem in request.form if "question" in elem]
        # questions = [elem for elem in dico if len(elem.split("_")) == 2]
        # questions = sorted(questions)
        # poids = [sorted([elem for elem in dico if "question_"+str(i)+"_poids" in elem and len(elem.split("_")) == 4])
        #          for i in range(1, len(questions)+1)]
        # reponses = [sorted([elem for elem in dico if "question_"+str(i)+"_reponse" in elem and len(elem.split("_")) == 4])
        #             for i in range(1, len(questions)+1)]
        # print(questions)
        # print(reponses)
        # print(poids)
        # questions = ["question_"+str(i+1) for i in range(len(questions))]
        # reponses = [["question_"+str(i+1)+"_reponse_"+str(j)
        #              for j in range(1, len(reponses[i])+1)] for i in range(len(reponses))]
        # poids = [["question_"+str(i+1)+"_poids_"+str(j) for j in range(1, len(poids[i])+1)] for i in range(len(poids))]
        # resultat = []
        # for i in range(len(questions)):
        #     # print("question "+str(i))
        #     # print(request.form[questions[i]])
        #     resultat.append({"question": request.form[questions[i]], "propositions": []})
        #     for j in range(len(reponses[i])):
        #         # print("réponse "+str(j))
        #         # print(request.form[reponses[i][j]])
        #         resultat[i]["propositions"].append({"reponse": request.form[reponses[i][j]],
        #                                             "poids":request.form[ poids[i][j]]})
        #         # print("poids "+str(j))
        #         # print(request.form[poids[i][j]])
        print("resultat", resultat)
        # print(questions)
        # print(reponses)
        # print(poids)
        # enregistrement fichier

        # with open("static/json_files/formulaire.json", "w") as f:
        #     json.dump(resultat, f)
        # enregistrement base de données
        praticien = sm.PraticienSess(session["pseudo"])
        praticien.creer_questionnaire(resultat)
        flash("Le questionnaire a correctement été enregistré.")
        # return send_from_directory("static/json_files", "formulaire.json", as_attachment=True,
        # mimetype="application/json")
        return jsonify(resultat)
    else:
        return jsonify([])


@main.route("/tcc/consulter_questionnaire", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def consulter_questionnaire():
    if request.method == "POST":
        print(request.form)
        if 'questionnaire' not in request.files:
            flash('No file part')
            return redirect(request.url)
        if "valider_questionnaire" in request.form:
            file = request.files['questionnaire']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('Aucun fichier sélectionné')
                return redirect(request.url)
            if file and allowed_file_json(file.filename):
                try:
                    print("on a passé ça")
                    # filename = secure_filename(file.filename)
                    questionnaire = json.loads(str(file.read(), encoding="utf8"))
                    session["questionnaire"] = questionnaire
                    session.modified = True
                    print(questionnaire)
                    return render_template("praticien/consultation_questionnaire.html", questionnaire=questionnaire,
                                           essage="ici")
                except:
                    return render_template("praticien/consultation_questionnaire.html", questionnaire=[],
                                           message="erreur")

    # TODO récupération questionnaire db
    if "questionnaire" in session:
        return render_template("praticien/consultation_questionnaire.html", questionnaire=session["questionnaire"],
                               message="ici")
    else:
        return render_template("praticien/consultation_questionnaire.html", message="debut")


@main.route("/tcc/modification_questionnaire", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def modification_questionnaire():
    if request.method == 'POST':
        print(request.form, request.files)
        # check if the post request has the file part
        if 'questionnaire' not in request.files:
            flash('No file part')
            return redirect(request.url)
        else:
            print(request.files)
            file = request.files['questionnaire']
            # if user does not select file, browser also
            # submit a empty part without filename
            if "valider_chargement_questionnaire" in request.form:
                print("on y est")
                if file.filename == '':
                    flash('Aucun fichier sélectionné')
                    return redirect(request.url)
                if file and allowed_file_json(file.filename):
                    try:
                        print("on a passé ça")
                        # filename = secure_filename(file.filename)
                        texte = str(file.read(), encoding="utf8")
                        print(texte)
                        questionnaire = json.loads(texte)
                        session["questionnaire"] = questionnaire
                        session.modified = True
                        print(questionnaire)
                        return render_template("praticien/questionnaire/modification_questionnaire.html",
                                               questionnaire=questionnaire, message="ici")

                    except:
                        return render_template("praticien/questionnaire/modification_questionnaire.html",
                                               message="questionnaire_invalide", questionnaire=[])
                else:
                    print("on est dans le sinon")
    else:
        # TODO récupération questionnaire db et modifier
        if "questionnaire" in session:
            return render_template("praticien/consultation_questionnaire.html", questionnaire=session["questionnaire"], message="ici")
        else:
            return render_template("praticien/questionnaire/modification_questionnaire.html", message="debut", questionnaire=[])


@main.route("/tcc/transmission_questionnaire", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien.html"))
def transmettre_questionnaire():
    if request.method == "POST":
        if "courriel" in request.form and "questionnaire" in request.form:
            if is_valid_email_address(request.form["courriel"]) and valide_questionnaire(request.form["questionnaire"]):
                # Générer un lien
                shuffle(alphabet_code)
                # code_genere = "".join([alphabet_code + str(time.time()).replace(".", "_")])
                # envoyer_email(request.form["courriel"], "clementbesnier.fr/tcc/repondre_questionnaire"+code_genere)
                # TODO, utiliser l'API Gmail pour envoyer le lien
                # TODO enregistrer le lien et le questionnaire en les associant

                return render_template("praticien/questionnaire/transmission_questionnaire.html", message="ok")
                pass
            else:
                # TODO à améliorer le diagnostique
                return render_template("praticien/questionnaire/transmission_questionnaire.html", message="courriel_invalide")

        else:
            return render_template("praticien/questionnaire/transmission_questionnaire.html")
    # TODO donner l'accès à la base données
    return render_template("praticien/questionnaire/transmission_questionnaire.html")


@main.route("/tcc/repondre_questionnaire/charger_fichier", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def repondre_questionnaire_charger_fichier():
    if request.method == "POST":
        print(request.form)
        file = request.files['questionnaire']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file_json(file.filename):
            print("on a passé ça")
            # filename = secure_filename(file.filename)
            questionnaire = json.loads(str(file.read(), encoding="utf8"))
            if valide_questionnaire(questionnaire):
                return render_template("repondre_questionnaire.html", questionnaire=questionnaire, message="ici")
            else:
                return render_template("repondre_questionnaire.html", questionnaire=[], message="questionnaire_invalide")
        else:
            return render_template("repondre_questionnaire.html", questionnaire=[], message="identi_invalide")
    else:

        return render_template("repondre_questionnaire.html", questionnaire=[], message="ici")


@main.route("/tcc/repondre_questionnaire/<string:identi>")
@validation_connexion_et_retour_defaut("pseudo_patient", redirect("/tcc/pas_connecte_patient"))
def repondre_questionnaire(identi):
    if request.method == "POST":
        if identi_existe(identi):
            resultat = request.form
            reponses = extraire_resultat_questionnaire(resultat)
            with open(os.path.join(DIRECTORY_JSON, identi), "r") as f:
                questionnaire = json.load(f)
                # TODO valider le questionnaire
                if valider_reponses_questionnaire(questionnaire, reponses):

                    return render_template("repondre_questionnaire.html",
                                           questionnaire=[], message="reponses_prises_en_compte")
        else:
            return render_template("repondre_questionnaire.html", questionnaire=[], message="identi_invalide")
    else:
        with open(os.path.join(DIRECTORY_JSON, identi), "r") as f:
            questionnaire = json.load(f)
        return render_template("repondre_questionnaire.html", questionnaire=questionnaire, message="")


@main.route("/tcc/traiter_reponse_questionnaire", methods=["GET", "POST"])
def traiter_reponse_questionnaire():
    return session["voca"].d  # TODO à créer filename


@main.route("/tcc/choisir_questionnaire")
def choisir_questionnaire():
    praticien = sm.PraticienSess(session["pseudo"])
    questionnaires = praticien.recuperer_questionnaires()
    return render_template("praticien/questionnaire/choisir_questionnaire.html", questionnaires=questionnaires)
