
from random import shuffle, sample
import time

from flask_wtf.csrf import CSRFError
from werkzeug.utils import secure_filename

from app.main.routes_utils import *
import app.sessions_manager as sm
from app.utils import *


#  Accueil
@main.route('/', methods=["POST", "GET"])
def index():
    # Sert à informer d'un événement particulier
    message = ""
    return render_template("index.html", message=message)


@main.route("/contact")
def contact():
    return render_template("contact.html")


@main.errorhandler(CSRFError)
def csrf_error(reason):
    return "Problème de CSRF",  400


@main.after_request
def add_cors_headers(response):
    r = request.referrer
    if r is not None:
        response.headers.add('Access-Control-Allow-Origin', r[:-1])
    # response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://127.0.0.1:5000'))
    return response


# @babel.localeselector
# def get_locale():
#     return request.accept_languages.best_match(Config.LANGUAGES.keys())

# @babel.timezoneselector
# def get_timezone():
#     user = getattr(g, 'user', None)
#     if user is not None:
#         return user.timezone


@main.route("/tcc/charger_suivi", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def charger_suivi():
    return render_template("praticien/demande_fichier_suivi_tcc.html")


# TODO to be modified
@main.route("/tcc/affichage_suivi", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def affichage_demande_suivi():
    if request.method == 'POST':
        print(request.form)
        # check if the post request has the file part
        if 'fichier_suivi' in request.files:
            print("on a un fichier")
            file = request.files['fichier_suivi']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                print("no selected file")
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file_json(file.filename):
                print("on a passé ça")
                filename = secure_filename(file.filename)
                texte = json.loads(str(file.read(), encoding="utf8"))

                # print(texte)
                corpus = dm.Corpus()
                corpus.from_json_app(texte)
                lignes = corpus.to_json()
                corpus.trier()
                # print("json : ", corpus.to_json())
                # with open(os.path.join(DIRECTORY_JSON_FILES, "transitoire_"+session["pseudo"]+".json"), "w") as f:
                #     json.dump(corpus.to_json(), f)
                session.modified = True
                # print('session', session)
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            print("aucun fichier")
            # flash('No file part')a
            # return redirect(request.url)

            print("selection_patient" in request.form)
            if "selection_patient" in request.form:
                selected_patient_id = request.form["selection_patient"]
                praticien_sess = sm.PraticienSess(session["pseudo"])
                ses_patients = praticien_sess.acceder_patients()
                selected_patient = ses_patients[int(selected_patient_id)-1]
                print("son patient", selected_patient)
                patient_sess = sm.PatientSess(selected_patient.email)
                # texte = patient_sess.to_json()

                lignes = patient_sess.tout_obtenir()
                # for ligne in lignes:
                #     print("lignes json", type(ligne))
                #     print("lignes json", ligne)

        if "affichage" in request.form:
            print("affichage")
            print(lignes)

            return render_template("praticien/analyse/affichage_fichier_suivi_tcc.html", lignes=lignes)

        if "affichage_pdf" in request.form:
            print("affichage_pdf")
            contenu = [{'text': 'Situations', "style": "header"}]
            # TODO récupérer les données et les mettre en format PDF pour pdfmaker
            # for entree in ["Entree", "prise_medicament"]:
            table1 = [["Date", "Heure", "Intensité", "Situation", "Emotions et sensations"]]
            for ligne in lignes["Entree"]:
                table1.append([ligne["date"],
                               ligne["heure"],
                               ligne["intensite"],
                               ligne["situation"],
                               ligne["emotions_sensations"]])
            contenu.append({"table": {"headerRows": 1, "widths": ['*', 'auto', 100, '*'], "body": table1}})
            contenu.append({"text": "Prise de médicament", "syle": "header"})
            table2 = [["Date", "Heure", "Médicament", "Dosage"]]
            for ligne in lignes["prise_medicament"]:
                table2.append([
                    ligne["date"],
                    ligne["heure"],
                    ligne["medicament"],
                    ligne["dosage"]
                ])
            contenu.append({"table": {"headerRows": 1, "widths": ['*', 'auto', 100, '*'], "body": table2}})
            data = {"content": contenu}
            return render_template("praticien/analyse/affichage_pdf_fichier_suivi_tcc.html", data=data)

        if "analyse" in request.form:
            print("Dans analyse")
            # TODO redirect
            vocabu = dm.Vocabulaire("")
            session["voca"] = '{}'
            vocabu.from_json(session["voca"])
            contenu = [{'text': 'Rapport', "style": "header"}]

            data_pdf = {"content": contenu}
            return render_template("praticien/analyse/analyse_fichier_suivi.html", dico=vocabu.d, champs=champs,
                                   lignes=lignes, types=champs, data_pdf=data_pdf)
        else:
            print("on est dans le sinon")
    praticien_sess = sm.PraticienSess(session["pseudo"])
    ses_patients = praticien_sess.acceder_patients()
    # print(ses_patients)
    return render_template("praticien/demande_fichier_suivi_tcc.html", patients=ses_patients)


# Gestion des données


@main.route("/tcc/ajax/exportation_donnees_appli", methods=['GET', 'POST'])
def exporter_ses_donnees():
    if "POST" == request.method:
        corpus = dm.Corpus()
        corpus.from_json_app(request.get_json())
        corpus.trier()
        print("json : ", corpus.to_json())
        with open(os.path.join(DIRECTORY_JSON, "transitoire_appli.json"), "w") as f:
            json.dump(corpus.to_json(), f)
        print('session', session)
        lignes = {"situation": corpus.get_situations(), "prise_medicament": corpus.get_prise_medicament()}
        unique = "".join(sample("azertyuiopqsdfghjklmwxcvbn", 10))+str(time.time()).split(".")[0]
        generer_pdf(unique, lignes)
        return URL+"/tcc/patient/export_pdf/"+unique+".pdf"


@main.route("/a_propos", methods=['GET'])
def a_propos():
    return render_template("a_propos.html")
