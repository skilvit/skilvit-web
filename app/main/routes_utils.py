
from flask import render_template, redirect, request, session, jsonify, send_file, send_from_directory, flash
import os
import json

from app import data_manager as dm
from app.utils import DIRECTORY_JSON
from . import main
from functools import wraps


__author__ = "Clément Besnier <skilvitapp@gmail.com>"


def validation_connexion_et_retour_defaut(pseudo, val):
    def deco(methode):
        @wraps(methode)
        def fonction_modifiee(*args, **kwargs):
            if pseudo in session:
                return methode(*args, **kwargs)
            else:
                return val
        return fonction_modifiee
    return deco


@main.route("/tcc/affichage_suivi_element/<string:type_element>/<int:indice>", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def afficher_suivi_element(type_element, indice):
    corpus = dm.Corpus()
    with open(os.path.join(DIRECTORY_JSON, "transitoire_"+session["pseudo"]+".json"), "r") as f:
        corpus.from_json_beau_format(json.load(f))

    print(session)
    print(corpus.champs)
    if type_element == "entree":
        return render_template("praticien/analyse/affichage_element_suivi_tcc.html",
                               element=corpus.get_situations()[indice])
    elif type_element == "pm":
        return render_template("praticien/analyse/affichage_element_suivi_tcc.html",
                               element=corpus.get_prise_medicament()[indice])


@main.route("/tcc/affichage_analyse_suivi", methods=["GET", "POST"])
@validation_connexion_et_retour_defaut("pseudo", redirect("/tcc/pas_connecte_praticien"))
def affichage_analyse_suivi():
    vocabu = dm.Vocabulaire("")
    vocabu.from_json(session["voca"])
    # corpus = dm.Corpus()
    # session["corpus_etudie"] = corpus.from_json(request.form[""])
    return render_template("praticien/analyse/analyse_fichier_suivi.html", dico=vocabu.d)


@main.route("/tcc/ajax/recuperer_vocabulaire", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo", {})
def recuperer_vocabulaire():
    vocabu = dm.Vocabulaire("")
    vocabu.from_json(session["voca"])
    return vocabu.d  # TODO à créer filename


@main.route("/tcc/ajax/calcul_correlation", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo", "<li> pas cool /li>")
def calculer_correlation():
    if "debut" in request.form and "mots_grandeur1" in request.form and "mots_grandeur2" in request.form:
        debut = dm.DateHeure.from_html_to_date(request.form["debut"])
        fin = dm.DateHeure.from_html_to_date(request.form["fin"])
        grandeurs1 = request.form["mots_grandeur1"]
        grandeurs2 = request.form["mots_grandeur2"]
        liste_mot_grandeur1 = grandeurs1.split(",")
        liste_mot_grandeur2 = grandeurs2.split(",")
        corpus = dm.Corpus()
        corpus.from_json_filename(session["corpus_etudie"])
        return "<li  class='ui-state-default'>"+"<p>Corrélations entre  de "+", ".join(liste_mot_grandeur1)+" et " + \
               ", ".join(liste_mot_grandeur2)+" entre le "+debut.beau_format_jour()+" et le "+fin.beau_format_jour() + \
               " : "+str(corpus.calcule_correlation(grandeurs1.split(","), grandeurs2.split(","), debut, fin)) + \
               ".</p></li>"
    else:
        return "<li> pas cool /li>"


@main.route("/tcc/ajax/calcul_frequence", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo", "<li  class='ui-state-default'> pas cool </li>")
def calculer_frequence():
    print(request.form)
    if "debut" in request.form and "fin" in request.form and \
            ('mots_grandeur1' in request.form or "theme_grandeur1" in request.form):
        # TODO vérfier que les données sont bonnes
        # print(request.form)
        debut = dm.DateHeure.from_html_to_date(request.form["debut"])
        print(debut.beau_format_jour())
        fin = dm.DateHeure.from_html_to_date(request.form["fin"])
        print(fin.beau_format_jour())
        mots_grandeur1 = request.form["mots_grandeur1"]
        # print(mots_grandeur1)
        # theme_grandeur1 = request.form["theme_grandeur1"]
        # print(theme_grandeur1)
        # print(corpus.calculer_frequence([mots_grandeur1], debut, fin))
        liste_mot_grandeur = mots_grandeur1.split(",")
        print(liste_mot_grandeur)
        corpus = dm.Corpus()
        corpus.from_json_filename(session["corpus_etudie"])
        frequence = corpus.calculer_frequence(liste_mot_grandeur, debut, fin)
        print(frequence)

        return "<li class='ui-state-default'>"+"<p>Occurrences de "+", ".join(liste_mot_grandeur)+" entre le " + \
               debut.beau_format_jour()+" et le "+fin.beau_format_jour()+" : "+str(frequence)+".</p></li>"
    else:
        print("pas cool")
        return "<li  class='ui-state-default'> pas cool </li>"


@main.route("/tcc/ajax/calcul_texte", methods=["POST", "GET"])
def afficher_texte():
    print(request.form)
    return "<li> à voir le commentaire donné</li>"


@main.route("/tcc/ajax/calcul_courbe", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo", {})
def calculer_courbe():
    if "debut" in request.form and "fin" in request.form and \
            ('mots_grandeur1' in request.form or "theme_grandeur1" in request.form):
        # TODO vérfier que les données sont bonnes
        print(request.form)
        debut = dm.DateHeure.from_html_to_date(request.form["debut"])
        fin = dm.DateHeure.from_html_to_date(request.form["fin"])
        _id = int(request.form["id"]) + 1
        mots_grandeur1 = request.form["mots_grandeur1"]
        corpus = dm.Corpus()
        corpus.from_json_filename(session["corpus_etudie"])
        # theme_grandeur1 = request.form["theme_grandeur1"]
        courbe = dm.Courbe(os.path.join(debut.format_jour_pour_fichier()+"_"+fin.format_jour_pour_fichier()+"_" +
                                        mots_grandeur1+".png"))
        data = courbe.charger_flot([date.beau_format_jour() for date in debut.liste_jours_entre_dates(fin)],
                                   corpus.calculer_occurrence_par_jour(mots_grandeur1, debut, fin))  # à remplir
        d = {"mots": mots_grandeur1, "debut": debut.beau_format_jour(), "fin": fin.beau_format_jour(),
             "data": data, "id": _id}
        return jsonify(d)
    else:
        return {}
    #     if type(mots_grandeur1) == str:
    #         return """<li class='ui-state-default'>
    #                     <p>Occurrences de """ + mots_grandeur1+""" entre le """+debut.beau_format_jour()+\
    #                     " et le "+fin.beau_format_jour()+""".</p>
    #                     <img class='element_rapport' id="""+str(_id)+
        # ' src='+ url_for('static', filename='images/'+courbe.filename)+"""></li>"""
    #
    #     elif type(mots_grandeur1) == list:
    #         return "<li class='ui-state-default'> <p>Occurrences de %s entre le %s et le </p> "
        #  % (", ".join(mots_grandeur1), debut.beau_format_jour(), fin.beau_format_jour())+
        # "<img class='element_rapport' id='%s' src='" % str(_id)+
        # url_for('static', filename='images/'+courbe.filename)+"></li>"
    # else:
    #     return "<li class='ui-state-default'>rien</li>"


@main.route("/tcc/ajax/recuperation_mots_par_theme", methods=["POST", "GET"])
@validation_connexion_et_retour_defaut("pseudo", "<option value=\"pas ok\"> pas ok</option>")
def recuperer_mots_par_theme():
    vocabu = dm.Vocabulaire("")
    vocabu.from_json(session["voca"])
    if request.form["theme"] in vocabu.d["themes"]:
        print("".join(["<option value="+mot+">"+mot+"</option>"
                       for mot in vocabu.d["themes"][request.form["theme"]]]))
        return " ".join(["<option value=\""+mot+"\">"+mot+"</option>"
                         for mot in vocabu.d["themes"][request.form["theme"]]])
    return "<option value=\"pas ok\"> pas ok</option>"
