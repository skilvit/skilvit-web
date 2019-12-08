# -*-coding:utf-8-*-
import datetime
import enum
import os

from flask_babel import to_utc, to_user_timezone, lazy_gettext

__author__ = ["Clément Besnier <admin@skilvit.fr>", ]

EMAIL_PATTERN = r"^[A-Za-z0-9\-_\.]+@[A-Za-z0-9\-_\.]+\.[a-z]{2,4}"
# Constantes


DIRECTORY_PROJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# if sys.platform == "win32":
DIRECTORY_IMAGES = os.path.join(DIRECTORY_PROJECT, "", "static", "images")
DIRECTORY_JSON = os.path.join(DIRECTORY_PROJECT, "", "static", "tmp", "json")  # "static/json_files"
DIRECTORY_TXT = os.path.join(DIRECTORY_PROJECT, "", "static", "tmp", "txt")  # "static/json_files"
DIRECTORY_CSV = os.path.join(DIRECTORY_PROJECT, "", "static", "tmp", "csv")  # "static/json_files"
DIRECTORY_TMP_PDF = os.path.join(DIRECTORY_PROJECT, "", "static", "tmp", "pdf")
DIRECTORY_TMP_LATEX = os.path.join(DIRECTORY_PROJECT, "", "static", "tmp", "latex")


champs = ["Entree", "prise_medicament"]
champs_entrees = ["type", "jour", "mois", "annee", "heure", "minute", "intensite", "situation", "emotions_sensations", "pensees", "taux_croyance", "pensee_alternative","taux_croyance_actualise", "comportement"]
champs_entrees_pour_tableau = ["type", "date", "heure", "intensite", "situation", "emotions_sensations", "pensees", "taux_croyance", "pensee_alternative","taux_croyance_actualise", "comportement"]
champs_entrees_pour_tableau_affichage = ["type", "date", "heure", "intensité", "situation", "émotions et sensations", "pensées", "taux de croyance", "pensée alternative","taux de croyance actualisé", "comportement"]
champs_prise_medicament = ["type", "jour", "mois", "annee", "heure", "minute", "medicament", "dosage"]
champs_prise_pour_tableau = ["type", "date", "heure", "medicament", "dosage"]
champs_prise_pour_tableau_affichage = ["type", "date", "heure", "médicament", "dosage"]

alphabet_code = "azertyuiopqsdfghjklmwxcvbn"
pseudo_mdp = {"clemsciences": "clemsciences"}
pseudo_patients_mdp = {"clemsciences": "clemsciences"}


def allowed_file_json(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ["json"]


class Sexe(enum.Enum):
    homme = 0
    femme = 1
    # indefini = 2

    def get_pretty_form(self):
        if self.value == Sexe.homme.value:
            return str(lazy_gettext("Homme"))
        elif self.value == Sexe.femme.value:
            return str(lazy_gettext("Femme"))


class EvenementSommeil(enum.Enum):
    coucher = 0
    lever = 1
    reveil_nuit = 2


class UniteMasse(enum.Enum):
    kg = 0



def is_valid_email_address(courriel):
    return True


def valide_questionnaire(questionnaire):
    return True


def valider_reponses_questionnaire(questionnaire, reponse):
    return True


def est_avant(t1, t2):
    maintenant = datetime.datetime.now()
    t1 = datetime.datetime.replace(maintenant, int(t1["annee"]), int(t1["mois"]), int(t1["jour"]), int(t1["heure"]),
                                   int(t1["minute"]))
    t2 = datetime.datetime.replace(maintenant, int(t2["annee"]), int(t2["mois"]), int(t2["jour"]), int(t2["heure"]),
                                   int(t2["minute"]))
    print(t1)
    print(t2)
    print((t2-t1).seconds)
    return t2 > t1


def trier(l):
    for i in range(len(l)-1):
        mini = i
        for j in range(i+1, len(l)):
            if est_avant(l[j], l[mini]):
                mini = j
        if mini != i:
            tampon = l[mini]
            l[mini] = l[i]
            l[i] = tampon
    return l


def extraire_resultat_questionnaire(res):
    """
    Sert à extraire les réponses de request.form vers

    :param res:
    :return:
    """
    pass


def identi_existe(pseudo):
    pass


def lire_config(config):
    d = {}
    with open(config, "r") as f:
        for line in f.readlines():
            d[line.split(":")[0]] = line.split(":")[1]
    return d


def generer_tableau_latex(lignes, titres, champs):
    """

    :param lignes:
    :param titres:
    :param champs:
    :return:
    """

    tableau = ""
    tableau += "\n\\begin{center}\n\\begin{longtable}{|"+"|".join(["Y" for i in range(len(titres))]) + "|}\n"
    tableau += "\n \hline "+"&".join([titre for titre in titres])+"\\\\"
    for ligne in lignes:
        tableau += "\\hline\n"+" & ".join([ligne[champ] for champ in champs])+"\\\\ \n"
    tableau += "\n \\hline \n \\end{longtable} \n \\end{center}"
    # len(lignes[0])
    # tableau += "\n\\begin{center}\n\\begin{longtable}{|" + "|".join(["c" for i in range(len(lignes[0]))]) + "|}\n"
    # for ligne in lignes:
    #     tableau += "\\hline\n" + "&".join([ligne[champ] for champ in champs_situation_tableau_latex]) + "\\\\"
    # tableau += "\n \\hline \n \\end{longtable} \n \\end{center}"
    return tableau


def generer_tableau_latex_site(lignes):
    """

    :param lignes:
    :return:
    """

    tableau = ""
    tableau += "\n\\begin{center}\n\\begin{longtable}{|"+"|".join(["Y" for i in range(10)]) + "|}\n"
    for ligne in lignes:
        print(ligne)
        tableau += "\\hline\n"+" & ".join([str(champ).replace("_", "-")+" : "+str(ligne[champ]) for champ in ligne if ligne[champ]])+"\\\\ \n"
    tableau += "\n \\hline \n \\end{longtable} \n \\end{center}"
    # len(lignes[0])
    # tableau += "\n\\begin{center}\n\\begin{longtable}{|" + "|".join(["c" for i in range(len(lignes[0]))]) + "|}\n"
    # for ligne in lignes:
    #     tableau += "\\hline\n" + "&".join([ligne[champ] for champ in champs_situation_tableau_latex]) + "\\\\"
    # tableau += "\n \\hline \n \\end{longtable} \n \\end{center}"
    return tableau


def generer_pdf(nom, d):
    """

    :param nom:
    :param titre:
    :param d:
    :return:
    """
    document = r"""
    \documentclass{article}
\usepackage[french]{babel}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{geometry}
\usepackage{wrapfig}
\usepackage{units}
\usepackage{ltxtable}
\usepackage{filecontents}
\usepackage{pbox}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{blindtext}
\usepackage{enumitem}
    \geometry{hmargin=2cm,vmargin=2cm}
    \date{\today}
    \title{Journal de bord TCC}
    \author{Skilvit}
    \begin{document}
    \newcolumntype{Y}{p{\dimexpr(\textwidth-7\arrayrulewidth-12\tabcolsep)/5\relax}}"""
    fin_document = "\n\\end{document}"
    titres = {
        "situation": ["Date", "Heure", "Intensité", "Situation", "Emotions et sensations"],
        "prise_medicament": ["Date", "Heure", "Médicament", "Dosage"]
    }
    champs = {
        "situation": ["date", "heure", "intensite", "situation", "emotions_sensations"],
        "prise_medicament": ["date", "heure", "medicament", "dosage"]
    }

    for cle in d:
        if len(d[cle]) > 0:
            document += generer_tableau_latex(d[cle], titres[cle], champs[cle])

    document += fin_document

    with open(os.path.join(DIRECTORY_TMP_LATEX, nom+".tex"), "w") as f:
        f.write(str(document))
    os.chdir(DIRECTORY_TMP_LATEX)
    ret = os.system("pdflatex " + os.path.join(DIRECTORY_TMP_LATEX, nom) + ".tex")
    if ret != 0:
        print("Erreur, pdflatex a échoué.")


def generer_pdf_site(nom, lignes):
    """

    :param nom:
    :param titre:
    :param d:
    :return:
    """
    document = r"""
    \documentclass{article}
\usepackage[french]{babel}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{geometry}
\usepackage{wrapfig}
\usepackage{units}
\usepackage{ltxtable}
\usepackage{filecontents}
\usepackage{pbox}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{blindtext}
\usepackage{enumitem}
    \geometry{hmargin=2cm,vmargin=2cm}
    \date{\today}
    \title{Journal de bord TCC}
    \author{Skilvit}
    \begin{document}
    \newcolumntype{Y}{p{\dimexpr(\textwidth-7\arrayrulewidth-12\tabcolsep)/5\relax}}"""
    fin_document = "\n\\end{document}"

    document += generer_tableau_latex_site(lignes)

    document += fin_document

    with open(os.path.join(DIRECTORY_TMP_LATEX, nom+".tex"), "w") as f:
        f.write(str(document))
    os.chdir(DIRECTORY_TMP_LATEX)
    ret = os.system("pdflatex " + os.path.join(DIRECTORY_TMP_LATEX, nom) + ".tex")
    if ret != 0:
        print("Erreur, pdflatex a échoué.")
    return ret
