# -*-coding:utf-8-*-
from typing import List

import nltk
from nltk.corpus import stopwords
import numpy as np
import abc

# import matplotlib.pyplot as plt

from app.database_manager import *

__author__ = ["Clément Besnier <admin@skilvit.fr>", ]

mots_trop_frequents = stopwords.words("french")


class Date:
    def __init__(self, jour, mois, annee):
        self.jour = jour
        self.mois = mois
        self.annee = annee

    @staticmethod
    def from_html_to_date(date_str: str):
        liste_date = date_str.split("-")
        jour = int(liste_date[2])
        mois = int(liste_date[1])
        annee = int(liste_date[0])
        return datetime.date(annee, mois, jour)

    @staticmethod
    def from_string_francais(date_str: str):
        liste_date = date_str.split("/")
        jour = int(liste_date[0])
        mois = int(liste_date[1])
        annee = int(liste_date[2])
        return DateHeure(jour=jour, mois=mois, annee=annee)

    # @staticmethod
    # def from_html_to_date(date_str):
    #     liste_date = date_str.split("-")
    #     jour = int(liste_date[2])
    #     mois = int(liste_date[1])
    #     annee = int(liste_date[0])
    #     return DateHeure(jour=jour, mois=mois, annee=annee, heure=1, minute=3)

    def beau_format_jour(self):
        ajout_jour = ""
        ajout_mois = ""
        if int(self.jour) < 10:
            ajout_jour = "0" + ajout_jour
        if int(self.mois) < 10:
            ajout_mois = "0" + ajout_mois
        return ajout_jour + str(self.jour) + "/" + ajout_mois + str(self.mois) + "/" + str(self.annee)

    def format_jour_pour_fichier(self):
        ajout_jour = ""
        ajout_mois = ""
        if int(self.jour) < 10:
            ajout_jour = "0" + ajout_jour
        if int(self.mois) < 10:
            ajout_mois = "0" + ajout_mois
        return ajout_jour + str(self.jour) + "-" + ajout_mois + str(self.mois) + "-" + str(self.annee)

    def nombre_de_jours_separant(self, autre_d):
        assert isinstance(autre_d, Date)
        d1 = datetime.datetime.today()
        d2 = datetime.datetime.today()
        d1 = d1.replace(year=self.annee, month=self.mois, day=self.jour)
        d2 = d2.replace(year=autre_d.annee, month=autre_d.mois, day=autre_d.jour)
        print(d1, d2)
        return (d2 - d1).days

    def liste_jours_entre_dates(self, autre_d):
        assert isinstance(autre_d, Date)
        d1 = datetime.datetime.today()
        d2 = datetime.datetime.today()
        d1 = d1.replace(self.annee, self.mois, self.jour)
        d2 = d2.replace(autre_d.annee, autre_d.mois, autre_d.jour)
        jours = []
        for i in range(d1.toordinal(), d2.toordinal() + 1):
            ordinal = datetime.datetime.fromordinal(i)
            jours.append(Date(ordinal.day, ordinal.month, ordinal.year))
        return jours


class Heure:
    def __init__(self, heure: int, minute: int):
        # assert heure < 24
        # assert minute < 60
        self.heure = heure
        self.minute = minute

    def beau_format_heure(self):
        if int(self.minute) < 10:
            return str(self.heure) + "h0" + str(self.minute)
        else:
            return str(self.heure) + "h" + str(self.minute)


class DateHeure(Date, Heure):
    def __init__(self, heure=None, minute=None, jour=None, mois=None, annee=None):
        Date.__init__(self, jour, mois, annee)
        Heure.__init__(self, heure, minute)
        self.heure = heure
        self.minute = minute
        self.jour = jour
        self.mois = mois
        self.annee = annee

    def __str__(self):
        return datetime.datetime(int(self.annee), int(self.mois), int(self.jour),
                                 int(self.heure), int(self.minute)).strftime("%H:%M %d/%m/%Y")

    def est_anterieur(self, autre_dh):
        assert isinstance(autre_dh, DateHeure)
        if self.annee < autre_dh.annee:
            return True
        elif self.annee > autre_dh.annee:
            return False
        else:
            if self.mois < autre_dh.mois:
                return True
            elif self.mois > autre_dh.mois:
                return False
            else:
                if self.jour < autre_dh.jour:
                    return True
                elif self.jour > autre_dh.jour:
                    return False
                else:
                    if self.heure < autre_dh.heure:
                        return True
                    elif self.heure > autre_dh.heure:
                        return False
                    else:
                        return self.minute <= autre_dh.minute

    @staticmethod
    def from_select_datetime(d: dict, label: str):
        print(d)
        heure = int(d["heure_" + label])
        minute = int(d["minute_" + label])
        jour = int(d["jour_" + label])
        mois = int(d["mois_" + label])
        annee = int(d["annee_" + label])
        return datetime.datetime(int(annee), int(mois), int(jour), int(heure), int(minute))

    @staticmethod
    def from_datepicker(d: dict, label: str):
        date = d["datetimepicker-date-input-" + label]
        date_s = date.split("/")
        if len(date_s) == 3:
            jour, mois, annee = date_s
        else:
            return None
        return datetime.datetime(int(annee), int(mois), int(jour), 0, 0)

    @staticmethod
    def from_datetimepicker(d: dict, label: str):
        date = d["datetimepicker-date-input-"+label]
        date_s = date.split("/")
        if len(date_s) == 3:
            jour, mois, annee = date_s
        else:
            return None
        hour = d["datetimepicker-hour-input-"+label]
        hour_s = hour.split(":")
        if len(hour_s) == 2:
            heure, minute = hour_s
        else:
            return None
        return datetime.datetime(int(annee), int(mois), int(jour), int(heure), int(minute))

    def from_dictionary_app(self, d: dict):
        """
        De l'application Android SKILVIT vers la date_heure
        :param d:
        :return:
        """
        print(d)
        self.heure = int(d["heure"])
        self.minute = int(d["minute"])
        self.jour = int(d["jour"])
        self.mois = int(d["mois"])
        self.annee = int(d["annee"])
        return datetime.datetime(int(self.annee), int(self.mois), int(self.jour), int(self.heure), int(self.minute))

    def from_dictionary_app_label(self, d: dict, label: str):
        print(d)
        self.heure = int(d["_".join(["heure", label])])
        self.minute = int(d["_".join(["minute"])])
        self.jour = int(d["_".join(["jour"])])
        self.mois = int(d["_".join(["mois"])])
        self.annee = int(d["_".join(["annee"])])
        return datetime.datetime(int(self.annee), int(self.mois), int(self.jour), int(self.heure), int(self.minute))

    def from_view_to_date(self, d: dict):
        """
        Des vues vers la date_heure
        :param d:
        :return:
        """
        s_date = d["date_heure"]
        date, heure = s_date.split('T')
        self.annne, self.mois, self.jour = date.split("-")
        self.heure, self.minute = heure.split(":")

    @staticmethod
    def from_view_to_datetime(date_str: str):
        """
        De la vue à datetime
        :param d: {"date_heure" :
        :return:
        """
        # date_str = d["entree_date"]
        print(date_str)
        date, heure = date_str.split('T')
        annee, mois, jour = date.split("-")
        heure, minute = heure.split(":")
        return datetime.datetime(int(annee), int(mois), int(jour), int(heure), int(minute))

    @staticmethod
    def from_firefox(date_str: str):
        print(date_str)
        date, heure = date_str.split(' ')
        annee, mois, jour = date.split("-")
        heure, minute, secondes = heure.split(":")
        return datetime.datetime(int(annee), int(mois), int(jour), int(heure), int(minute), int(secondes))

    def from_dictionary_beau_format(self, d: dict):
        """

        :param d: {"heure": "00h00", "date": "00/00/00"}
        :return:
        """
        heures = d["heure"].split("h")
        if len(heures) == 2:
            heure, minute = d["heure"].split("h")
        else:
            heure = heures
            minute = 0
        jour, mois, annee = d["date"].split("/")
        self.heure = int(heure)
        self.minute = int(minute)
        self.jour = int(jour)
        self.mois = int(mois)
        self.annee = int(annee)

    def from_datetime(self, dt):
        self.heure = dt.hour
        self.minute = dt.minute
        self.annee = dt.year
        self.mois = dt.month
        self.jour = dt.day


# ---------champs----------
class Champ:
    def __init__(self, _type):
        self.id = -1
        self.type = _type
        self.date_heure = DateHeure()

    @abc.abstractmethod
    def from_view_to_data(self, post):
        """
        Des vues de l'interface web aux données définies dans data_manager
        (en gros on remplit les attributs depuis un POST)
        :return:
        """
        return

    @abc.abstractmethod
    def from_dictionary(self, d):
        """

        :return:
        """
        return

    @abc.abstractmethod
    def from_database(self, db_src):
        """
        De la base de données à data_manager.py

        :return:
        """
        return

    @abc.abstractmethod
    def to_dictionary(self):
        """
        A partir des attributs de la classe, on retourne un dctionnaire simili bd
        :return:
        """
        return

    @abc.abstractmethod
    def from_dictionary_app(self, champ):
        return


class Alimentation(Champ):
    def __init__(self):
        Champ.__init__(self, "alimentation")
        self.repas = None
        self.nourriture = None

        # self.info = {}

    def from_view_to_data(self, post: dict):
        self.date_heure = to_utc(DateHeure.from_datetimepicker(post, ""))
        self.repas = post["repas"]
        self.nourriture = post["nourriture"]

    def from_dictionary(self, d: dict):
        self.date_heure = DateHeure.from_view_to_datetime(d["date_heure"])
        self.repas = d["repas"]
        self.nourriture = d["nourriture"]
        if "id" in d:
            self.id = d["id"]

    def from_database(self, acti_phy_db):
        # self._type = "alimentation"
        self.date_heure = DateHeure()
        self.date_heure.from_datetime(to_user_timezone(acti_phy_db.date_heure))
        self.repas = acti_phy_db.repas
        self.nourriture = acti_phy_db.nourriture
        self.id = acti_phy_db.get_id()

    def to_dictionary(self):
        return {"type": self.type,
                "repas": self.repas,
                "nourriture": self.nourriture,
                "date": self.date_heure.beau_format_jour(),
                "heure": self.date_heure.beau_format_heure(),
                "id": self.id}

    def from_dictionary_app(self, champ: dict):
        self.date_heure.from_dictionary_app(champ)
        self.nourriture = champ["nourriture"]
        self.repas = champ["repas"]


class ActivitePhysique(Champ):
    def __init__(self):
        Champ.__init__(self, "activite_physique")
        self.sport = None
        self.duree = None
        self.difficulte_ressentie = None
        # self.info = {}

    def from_view_to_data(self, post: dict):
        self.date_heure = to_utc(DateHeure.from_datetimepicker(post, ""))
        self.sport = post["sport"]
        self.duree = post["duree"]
        self.difficulte_ressentie = post["difficulte_ressentie"]
        # self.valeur = d["type"]
        # self.info = d

    def from_dictionary(self, d: dict):
        self.date_heure = DateHeure.from_view_to_datetime(d["date_heure"])
        self.sport = d["sport"]
        self.duree = d["duree"]
        self.difficulte_ressentie = d["difficulte_ressentie"]
        # self.valeur = d["type"]
        # self.info = d
        if "id" in d:
            self.id = d["id"]

    def from_database(self, acti_phy_db):
        # self.type = "activite_physique"
        self.date_heure = DateHeure()
        self.date_heure.from_datetime(to_user_timezone(acti_phy_db.date_heure))
        self.difficulte_ressentie = acti_phy_db.difficulte_ressentie
        self.sport = acti_phy_db.sport
        self.duree = acti_phy_db.duree
        self.id = acti_phy_db.get_id()

    def to_dictionary(self):
        return {"type": self.type,
                "sport": self.sport,
                "duree": self.duree,
                "difficulte_ressentie": self.difficulte_ressentie,
                "date": self.date_heure.beau_format_jour(),
                "heure": self.date_heure.beau_format_heure(),
                "id": self.id}

    def from_dictionary_app(self, champ: dict):
        self.date_heure = DateHeure()
        self.date_heure.from_dictionary_app(champ)
        self.sport = champ["sport"]
        self.duree = champ["duree"]
        self.difficulte_ressentie = champ["difficulte_ressentie"]


class Glycemie(Champ):
    def __init__(self):
        Champ.__init__(self, "glycemie")
        self.glycemie = None

    def from_view_to_data(self, post: dict):
        self.date_heure = to_utc(DateHeure.from_datetimepicker(post, ""))
        self.glycemie = post["glycemie"]

    def from_dictionary(self, d: dict):
        self.date_heure.from_dictionary_beau_format(d)
        self.glycemie = d["glycemie"]
        if "id" in d:
            self.id = d["id"]

    def from_database(self, glycemie_db):
        self.date_heure = DateHeure()
        self.date_heure.from_datetime(to_user_timezone(glycemie_db.date_heure))
        self.glycemie = glycemie_db.glycemie
        self.id = glycemie_db.get_id()

    def to_dictionary(self):
        return {"type": self.type,
                "glycemie": self.glycemie,
                "date": self.date_heure.beau_format_jour(),
                "heure": self.date_heure.beau_format_heure(),
                "id": self.id}

    def from_dictionary_app(self, champ: dict):
        self.date_heure = DateHeure()
        self.date_heure.from_dictionary_app(champ)
        self.glycemie = champ["glycemie"]


class Masse(Champ):
    def __init__(self):
        Champ.__init__(self, "masse")
        self.masse = None
        self.unite_masse = UniteMasse.kg

    def from_view_to_data(self, d: dict):
        """
        statique
        :param d:
        :return: data, list of sleep event
        """
        self.date_heure = to_utc(DateHeure.from_datetimepicker(d, ""))
        self.masse = d["masse"]
        self.unite_masse = d["unite_masse"]

    def from_dictionary(self, d: dict):
        self.date_heure.from_dictionary_beau_format(d)
        self.masse = d["masse"]
        self.unite_masse = d["unite_masse"]
        if "id" in d:
            self.id = d["id"]

    def from_database(self, poids_db):
        self.date_heure = DateHeure()
        self.date_heure.from_datetime(to_user_timezone(poids_db.date_heure))
        self.masse = poids_db.masse
        self.unite_masse = poids_db.unite_masse.name
        self.id = poids_db.get_id()

    def to_dictionary(self):
        return {"type": self.type,
                "masse": self.masse,
                "unite_masse": self.unite_masse,
                "date": self.date_heure.beau_format_jour(),
                "heure": self.date_heure.beau_format_heure(),
                "id": self.id}

    def from_dictionary_app(self, champ: dict):
        self.date_heure = DateHeure()
        self.date_heure.from_dictionary_app(champ)
        self.masse = champ["masse"]
        self.unite_masse = champs["unite_masse"]


class Sommeil(Champ):
    def __init__(self):
        Champ.__init__(self, "sommeil")
        self.date_heure_coucher = None
        self.date_heure_lever = None
        self.heure_reveil_dans_nuit = None
        self.commentaire = None
        self.date_heure_evenement = None
        self.evenement = None

    def from_new_webview(self, forme: dict):
        self.date_heure = DateHeure.from_select_datetime(forme, "")
        self.date_heure_evenement = DateHeure.from_select_datetime(forme, "evenement")
        self.evenement = forme["evenement"]
        self.commentaire = forme["commentaire"]

    def from_view_to_data(self, d: dict):
        """
        statique
        :param d:
        :return: data, list of sleep event
        """
        # data = []
        self.date_heure = to_utc(DateHeure.from_datetimepicker(d, ""))
        self.date_heure_coucher = DateHeure.from_datetimepicker(d, "coucher")
        self.date_heure_lever = DateHeure.from_datetimepicker(d, "lever")
        self.date_heure_lever = DateHeure.from_datetimepicker(d, "reveil_nuit")
        self.commentaire = d["commentaire"]
        # for evenement in ["heure_coucher", "heure_lever", "heure_coucher", "heure_reveil_dans_nuit"]:
        #     if evenement in d:
        #         nouveau_sommeil = Sommeil()
        #         self.evenement = evenement
        #         self.date_heure = DateHeure.from_view_to_datetime(d[evenement])
        #         data.append(nouveau_sommeil)
        # return data

    def from_dictionary(self, d: dict):
        self.date_heure.from_dictionary_beau_format(d)
        self.date_heure_coucher.from_dictionary_beau_format(d)
        self.date_heure_lever.from_dictionary_beau_format(d)
        self.commentaire = d["commentaire"]
        if "id" in d:
            self.id = d["id"]

    def from_database(self, sommeil_db):
        self.type = "sommeil"
        self.date_heure = DateHeure()
        self.date_heure.from_datetime(to_user_timezone(sommeil_db.date_heure))
        self.date_heure_evenement = DateHeure()
        self.date_heure_evenement.from_datetime(to_user_timezone(sommeil_db.date_heure_evenement))
        self.evenement = sommeil_db.evenement
        self.commentaire = sommeil_db.commentaire
        self.id = sommeil_db.get_id()

    def to_dictionary(self):
        return {"type": self.type,
                "date_heure": self.date_heure.beau_format_jour(),
                "date_heure_evenement": self.date_heure_evenement.beau_format_heure(),
                "evenement": self.evenement,
                "commentaire": self.commentaire,
                "id": self.id
                }

    def from_dictionary_app(self, champ: dict):
        self.date_heure = DateHeure()
        self.date_heure.from_dictionary_app(champ)
        self.date_heure_coucher = DateHeure()
        self.date_heure_coucher.from_dictionary_app_label(champ, "coucher")
        self.date_heure_lever = DateHeure()
        self.date_heure_lever.from_dictionary_app_label(champ, "lever")
        self.commentaire = champ["commentaire"]


class PriseMedicament(Champ):
    def __init__(self):
        Champ.__init__(self, "prise_medicament")
        self.id = -1
        self.medicament = None
        self.dosage = None
        self.valeur = None

    def from_view_to_data(self, d: dict):
        self.date_heure = to_utc(DateHeure.from_datetimepicker(d, ""))
        self.dosage = d["dosage"]
        self.medicament = d["medicament"]

    def from_dictionary(self, d: dict):
        print(d)
        if "id" in d:
            self.id = d["id"]
        self.date_heure = DateHeure()
        self.date_heure.from_dictionary_app(d)
        self.dosage = d["dosage"]
        self.medicament = d["medicament"]

    def from_database(self, pm_db):
        self.id = pm_db.get_id()
        self.date_heure = DateHeure()
        self.date_heure.from_datetime(to_user_timezone(pm_db.date_heure))
        self.dosage = pm_db.dosage
        self.medicament = pm_db.medicament

    def from_dictionary_beau_format(self, d: dict):
        self.date_heure.from_dictionary_beau_format(d)
        self.dosage = d["dosage"]
        self.medicament = d["medicament"]

    def to_dictionary(self):
        return {"dosage": self.dosage,
                "type": self.type,
                "medicament": self.medicament,
                "date": self.date_heure.beau_format_jour(),
                "heure": self.date_heure.beau_format_heure(),
                "id": self.id}

    def from_dictionary_app(self, champ: dict):
        self.date_heure = DateHeure()
        self.date_heure.from_dictionary_app(champ)
        self.dosage = champ["dosage"]
        self.medicament = champ["medicament"]


class Situation(Champ):
    def __init__(self):
        Champ.__init__(self, "situation")
        self.id = -1
        self.emotions_sensations = None
        self.situation = None
        self.intensite = None
        self.pensees = None
        self.taux_croyance = None
        self.pensee_alternative = None
        self.taux_croyance_actualise = None
        self.comportement = None

    # def from_json(self, filename):
    #     with open(filename, "r")as f:
    #         d = json.load(f)
    #         self.from_dictionary(d)
    def from_view_to_date(self, d: dict):
        self.date_heure = DateHeure()
        self.date_heure.from_select_datetime(d, "")
        self.emotions_sensations = d["entree_emotions"] + " " + d["entree_sensations"]
        self.situation = d["entree_situation"]
        self.intensite = d["entree_intensite"]
        self.pensees = d["entree_pensees"]
        if "taux_croyance" in d:
            self.taux_croyance = d["entree_taux_croyance"]
            self.pensee_alternative = d["entree_pensee_alternative"]
            self.taux_croyance_actualise = d["entree_taux_croyance_actualise"]
        self.comportement = d["entree_comportement"]

    def from_view_to_data(self, d: dict):
        print("d", d)
        self.date_heure = to_utc(DateHeure.from_datetimepicker(d, ""))
        print(self.date_heure)
        self.emotions_sensations = d["emotions_sensations"]
        self.situation = d["situation"]
        self.intensite = d["intensite"]
        self.pensees = d["pensees"]
        if "taux_croyance" in d:
            self.taux_croyance = d["taux_croyance"]
            self.pensee_alternative = d["pensee_alternative"]
            self.taux_croyance_actualise = d["taux_croyance_actualise"]
        self.comportement = d["comportement"]
        # if "valeur" in d:
        #     self.valeur = "situation"
        # else:
        #     self.valeur = "situation"

    def to_dictionary(self):
        return {"type": self.type,
                "date": self.date_heure.beau_format_jour(),
                "heure": self.date_heure.beau_format_heure(),
                "emotions_sensations": self.emotions_sensations,
                "situation": self.situation,
                "intensite": self.intensite,
                "pensees": self.pensees,
                "taux_croyance": self.taux_croyance,
                "pensee_alternative": self.pensee_alternative,
                "taux_croyance_actualise": self.taux_croyance_actualise,
                "comportement": self.comportement,
                "id": self.id}

    def from_dictionary(self, d: dict):
        print(d)
        # self.date_heure = DateHeure()
        if "id" in d:
            self.id = d["id"]
        self.date_heure = DateHeure.from_view_to_datetime(d)  # from_dictionary_app(d)
        self.emotions_sensations = d["emotions_sensations"]
        self.situation = d["situation"]
        self.intensite = d["intensite"]
        self.pensees = d["pensees"]
        if "taux_croyance" in d:
            self.taux_croyance = d["taux_croyance"]
            self.pensee_alternative = d["pensee_alternative"]
            self.taux_croyance_actualise = d["taux_croyance_actualise"]
        self.comportement = d["comportement"]

    def from_database(self, situation_db):
        self.id = situation_db.get_id()
        self.date_heure = DateHeure()
        self.date_heure.from_datetime(to_user_timezone(situation_db.date_heure))
        self.emotions_sensations = situation_db.emotions_sensations
        self.situation = situation_db.situation
        self.intensite = situation_db.intensite
        self.pensees = situation_db.pensees
        # if "taux_croyance" in situation_db.info:
        self.taux_croyance = situation_db.taux_croyance
        self.pensee_alternative = situation_db.pensee_alternative
        self.taux_croyance_actualise = situation_db.taux_croyance_actualise
        self.comportement = situation_db.comportement

    def from_dictionary_beau_format(self, d: dict):
        if "id" in d:
            self.id = d["id"]
        self.date_heure.from_dictionary_beau_format(d)
        self.emotions_sensations = d["emotions_sensations"]
        self.situation = d["situation"]
        self.intensite = d["intensite"]
        self.pensees = d["pensees"]
        self.taux_croyance = d["taux_croyance"]
        self.pensee_alternative = d["pensee_alternative"]
        self.taux_croyance_actualise = d["taux_croyance_actualise"]
        self.comportement = d["comportement"]

    def en_texte(self):
        return ("Le " + self.date_heure.beau_format_jour() + " à " + self.date_heure.beau_format_heure() + ". " +
                self.situation + " " + self.emotions_sensations + " " + self.pensees + " " + self.comportement)

    def calcule_occurrences_unigrammes(self):
        contenu_texte = self.en_texte()
        # print(texte)
        phrases = nltk.sent_tokenize(contenu_texte, "french")
        mots = [mot.lower() for mot in nltk.word_tokenize(contenu_texte, "french")]
        # print(mots)
        occurrences = nltk.FreqDist()
        occurrences.update(mots)
        return occurrences

    def calcule_occurrences_unigrammes_sans_mots_trop_frequents(self):
        contenu_texte = self.en_texte()
        # print(texte)
        phrases = nltk.sent_tokenize(contenu_texte, "french")

        mots = [mot.lower() for mot in nltk.word_tokenize(contenu_texte, "french") if mot.lower() not in mots_trop_frequents]
        # print(mots)
        occurrences = nltk.FreqDist()
        occurrences.update(mots)
        return occurrences

    def calcule_occurrences_bigrammes(self):
        # TODO à changer
        contenu_texte = self.en_texte()
        phrases = nltk.sent_tokenize(contenu_texte, "french")
        mots = nltk.word_tokenize(contenu_texte, "french")
        bigr_mots = nltk.bigrams(mots)
        occurrences = nltk.FreqDist()
        occurrences.update(bigr_mots)
        return occurrences

    def from_dictionary_app(self, champ: dict):
        self.date_heure = DateHeure()
        self.date_heure.from_dictionary_app(champ)
        self.emotions_sensations = champ["emotions_sensations"]
        self.situation = champ["situation"]
        self.intensite = champ["intensite"]
        self.pensees = champ["pensees"]
        self.taux_croyance = champ["taux_croyance"]
        self.pensee_alternative = champ["pensee_alternative"]
        self.taux_croyance_actualise = champ["taux_croyance_actualise"]
        self.comportement = champ["comportement"]


# --------- fin champs ----------


class Courbe:
    def __init__(self, filename: str):
        self.filename = filename

    def charger(self, abscisses: List, ordonnees: List, titre="", grandeur_x="", grandeur_y=""):
        plt.title(titre)
        print(len(abscisses), len(ordonnees))
        plt.axis([0, len(abscisses), min(ordonnees), max(ordonnees) + 1])
        plt.grid(True)
        plt.xlabel(grandeur_x)
        plt.ylabel(grandeur_y)
        plt.hist(ordonnees, bins=len(abscisses))
        plt.savefig(os.path.join(DIRECTORY_PROJECT, "static", "images", self.filename))
        plt.close()

    def charger_flot(self, abscisses: List, ordonnees: List, titre="", grandeur_x="", grandeur_y=""):
        return [(i, ordonnees[i]) for i in range(len(abscisses))]


class Corpus:
    def __init__(self):
        # self.filename = None
        self.champs = []

    # def get_filename(self):
    #     return {"filename": os.path.join("suivis", self.filename)}

    def to_json(self):
        return json.dumps([champ.to_dictionary() for champ in self.champs])

    def from_json_filename(self, filename: dict):
        with open(filename["filename"], "r", encoding="utf8") as f:
            self.from_json(f.read())

    def from_json(self, serialized_corpus: dict):
        print(serialized_corpus)
        # print("serialized_corpus", serialized_corpus)
        serialized_d = json.loads(serialized_corpus)
        for serialized_champ in serialized_d:
            if "type" in serialized_champ:
                if serialized_champ["type"] == "Entree":
                    e = Situation()
                    e.from_dictionary(serialized_champ)
                    self.champs.append(e)
                elif serialized_champ["type"] == "prise_medicament":
                    pm = PriseMedicament()
                    pm.from_dictionary(serialized_champ)
                    self.champs.append(pm)
                else:
                    print("problème data")

    def from_json_beau_format(self, serialized_corpus: dict):
        print(serialized_corpus)
        # print("serialized_corpus", serialized_corpus)
        serialized_d = json.loads(serialized_corpus)
        for serialized_champ in serialized_d["champs"]:
            print(serialized_champ)
            if "type" in serialized_champ:
                if serialized_champ["type"] == "Entree":
                    e = Situation()
                    e.from_dictionary_beau_format(serialized_champ)
                    self.champs.append(e)
                elif serialized_champ["type"] == "prise_medicament":
                    pm = PriseMedicament()
                    pm.from_dictionary_beau_format(serialized_champ)
                    self.champs.append(pm)
                else:
                    print("problème data")
        print(self.champs)

    def from_json_app(self, texte: dict):

        valeurs = texte  # json.loads(texte, encoding="utf8")
        # print(valeurs)
        for champ in valeurs:
            if champ["type"] == "situation":
                e = Situation()
                e.from_dictionary_app(champ)
                self.ajout_champ(e)

            elif champ["type"] == "prise_medicament":
                pm = PriseMedicament()
                pm.from_dictionary_app(champ)
                self.ajout_champ(pm)

            elif champ["type"] == "activite_physique":
                ap = ActivitePhysique()
                ap.from_dictionary_app(champ)
                self.ajout_champ(ap)

            elif champ["type"] == "sommeil":
                sommeil = Sommeil()
                sommeil.from_dictionary_app(champ)
                self.ajout_champ(sommeil)

            elif champ["type"] == "alimentation":
                alimentation = Alimentation()
                alimentation.from_dictionary_app(champ)
                self.ajout_champ(alimentation)

            elif champ["type"] == "glycemie":
                gl = Glycemie()
                gl.from_dictionary_app(champ)
                self.ajout_champ(gl)

            elif champ["type"] == "masse":
                gl = Masse()
                gl.from_dictionary_app(champ)
                self.ajout_champ(gl)

    def charger_champs_db(self, id_patient: int):

        situations_db = SituationDB.query.filter_by(id_patient=id_patient)
        for sdb in situations_db:
            e = Situation()
            e.from_database(sdb)
            self.ajout_champ(e)

        prises_medicament_db = PriseMedicamentDB.query.filter_by(id_patient=id_patient)
        for pmdb in prises_medicament_db:
            pm = PriseMedicament()
            pm.from_database(pmdb)
            self.ajout_champ(pm)

        alimentations_db = AlimentationDB.query.filter_by(id_patient=id_patient)
        for ali_db in alimentations_db:
            ali = Alimentation()
            ali.from_database(ali_db)
            self.ajout_champ(ali)

        activites_physiques_db = ActivitePhysiqueDB.query.filter_by(id_patient=id_patient)
        for acti_phy_db in activites_physiques_db:
            acti_phy = ActivitePhysique()
            acti_phy.from_database(acti_phy_db)
            self.ajout_champ(acti_phy)

        sommeils_db = SommeilDB.query.filter_by(id_patient=id_patient)
        for sommeil_db in sommeils_db:
            som = Sommeil()
            som.from_database(sommeil_db)
            self.ajout_champ(som)

        poids_db = MasseDB.query.filter_by(id_patient=id_patient)
        for pdb in poids_db:
            masse = Masse()
            masse.from_database(pdb)
            self.ajout_champ(masse)

        glycemie_db = GlycemieDB.query.filter_by(id_patient=id_patient)
        for gdb in glycemie_db:
            glycemie = Glycemie()
            glycemie.from_database(gdb)
            self.ajout_champ(glycemie)

    def ajout_champ(self, champ: dict):
        assert isinstance(champ, Champ)
        self.champs.append(champ)

    def calcule_correlation(self, grandeurs1: str, grandeurs2: str, debut, fin):
        assert isinstance(debut, DateHeure)
        assert isinstance(fin, DateHeure)
        assert debut.est_anterieur(fin)
        vec1 = np.array(self.calculer_occurrence_par_jour(grandeurs1, debut, fin))
        vec2 = np.array(self.calculer_occurrence_par_jour(grandeurs2, debut, fin))
        print(vec1)
        print(vec2)
        if np.sum(vec1) == 0 or np.sum(vec2) == 0:
            return 0.
        print(vec1)
        print(vec2)

        return np.sum(vec1 * vec2) / (np.sum(vec1) * np.sum(vec2))

    def calculer_frequence(self, grandeurs, debut, fin):
        assert isinstance(debut, DateHeure)
        assert isinstance(fin, DateHeure)
        assert debut.est_anterieur(fin)
        print('champs : ', self.champs)
        entrees = [champ for champ in self.champs if champ.valeur == "Entree" and
                   debut.est_anterieur(champ.date_heure) and champ.date_heure.est_anterieur(fin)]
        # print([jour.beau_format_jour() for jour in debut.liste_jours_entre_dates(fin)])
        occ_uni = nltk.FreqDist()
        # occ_bi = nltk.FreqDist()
        print("entrees : ", entrees)
        for entree in entrees:
            print(entree.en_texte())
            # print(entree.calcule_occurrences_unigrammes())
            occ_uni.update(entree.calcule_occurrences_unigrammes_sans_mots_trop_frequents())
            # occ_bi.update(entree.calcule_occurrences_unigrammes())
        print(occ_uni)
        print(grandeurs)
        return sum([occ_uni[grandeur.strip()] for grandeur in grandeurs])

    def calculer_occurrence_par_jour(self, grandeurs, debut, fin):
        assert isinstance(debut, DateHeure)
        assert isinstance(fin, DateHeure)
        assert debut.est_anterieur(fin)
        if type(grandeurs) == str:
            grandeurs = [grandeurs]
        entrees = [champ for champ in self.champs if champ.valeur == "Entree" and
                   debut.est_anterieur(champ.date_heure) and champ.date_heure.est_anterieur(fin)]
        print([entree.date_heure.beau_format_jour() for entree in entrees])
        # print(debut.nombre_de_jours_separant(fin))
        occ_uni_par_jour = []
        # self.occ_bi = []
        for date_heure in debut.liste_jours_entre_dates(fin):
            freq_uni = nltk.FreqDist()
            for i, entree in enumerate(entrees):
                # print(entree.date_heure.beau_format_jour(), date_heure.beau_format_jour())
                if entree.date_heure.beau_format_jour() == date_heure.beau_format_jour():
                    occu_entree = entree.calcule_occurrences_unigrammes_sans_mots_trop_frequents()
                    # print(occu_entree)
                    freq_uni.update(occu_entree)
                    # print(freq_uni)
                    # freq_bi = nltk.FreqDist(entree.calcule_occurrences_bigrammes())

            occ_uni_par_jour.append(sum([freq_uni[grandeur] for grandeur in grandeurs]))
            # self.occ_bi.append(sum([freq_bi[grandeur] for grandeur in grandeurs]))
        print(occ_uni_par_jour)
        return occ_uni_par_jour  # , self

    def liste_intensite(self, debut, fin):
        entrees = [champ for champ in self.champs if champ.valeur == "Entree" and
                   debut.est_anterieur(champ.date_heure) and champ.date_heure.est_anterieur(fin)]
        # print(debut.nombre_de_jours_separant(fin))
        intensites = []
        for i, entree in enumerate(entrees):
            intensites.append(entree.intensite)
        return intensites  # , self

    # def resumer(self, taille_max, debut, fin):
    #     assert isinstance(debut, DateHeure)
    #     assert isinstance(fin, DateHeure)
    #     assert debut.est_anterieur(fin)

    def trier(self):
        for i in range(len(self.champs) - 1):
            mini = i
            for j in range(i + 1, len(self.champs)):
                if self.champs[j].date_heure.est_anterieur(self.champs[mini].date_heure):
                    mini = j
            if mini != i:
                self.champs[i], self.champs[mini] = self.champs[mini], self.champs[i]
        return self.champs

    def get_field(self, _class):
        return [champ.to_dictionary() for champ in self.champs if isinstance(champ, _class)]

    def get_situations(self):
        return self.get_field(Situation)

    def get_prise_medicament(self):
        return self.get_field(PriseMedicament)

    def get_activite_physique(self):
        return self.get_field(ActivitePhysique)

    def get_sommeil(self):
        return self.get_field(Sommeil)

    def get_alimentation(self):
        return self.get_field(Alimentation)

    def get_glycemie(self):
        return self.get_field(Glycemie)

    def get_poids(self):
        return self.get_field(Masse)


class Vocabulaire:
    def __init__(self, filename: str):
        self.filename = filename
        self.d = None  # collections.defaultdict()

    def initialiser_vocabulaire(self):
        if not os.path.isfile(self.filename):
            with open(self.filename, "w") as f:
                d = {"mots": [], "themes": {}}
                json.dump(d, f)

    def lire_vocabulaire(self):
        with open(self.filename, "r", encoding="utf8") as f:
            vocabulaire = json.load(f)
            if "mots" in vocabulaire and "themes" in vocabulaire:
                self.d = vocabulaire
            else:
                self.d = None

    def ajouter_mot(self, mot: str):
        if self.d is not None:
            self.d["mots"].append(mot)

    def ajouter_mots(self, mots: List[str]):
        if self.d is not None:
            self.d["mots"].extend(mots)

    def ajouter_nouveau_theme(self, theme: str):
        if self.d is not None:
            self.d["themes"][theme] = []

    def ajouter_mot_a_theme(self, mot: str, theme: str):
        if self.d is not None:
            self.d["themes"][theme].append(mot)

    def ajouter_mots_a_theme(self, mots: List, theme: str):
        if self.d is not None:
            self.d["themes"][theme].extend(mots)

    def to_json(self):
        return json.dumps({"filename": self.filename, "d": self.d})

    # def from_json(self, d):
    #     d_vocabu = json.loads(d)
    #     self.d = {"themes": {}, "mots": {}}
    #     # self.d = d_vocabu["d"]
    #     # self.filename = d_vocabu["filename"]
    #     self.filename = "je sais pas"


class Questionnaire:
    def __init__(self):
        pass

    def from_json_to_list(self):
        pass


def get_profil_patient(id_patient: int):
    return PatientDB.row_to_dict(id_patient)


def get_entrees_patient(id_patient: int):
    situations_db = SituationDB.query.filter_by(id_patient=id_patient)
    entrees = []
    for sdb in situations_db:
        e = Situation()
        e.from_database(sdb)
        entrees.append(e.to_dictionary())

    prises_medicament_db = PriseMedicamentDB.query.filter_by(id_patient=id_patient)
    for pmdb in prises_medicament_db:
        pm = PriseMedicament()
        pm.from_database(pmdb)
        entrees.append(pm.to_dictionary())

    alimentations_db = AlimentationDB.query.filter_by(id_patient=id_patient)
    for ali_db in alimentations_db:
        ali = Alimentation()
        ali.from_database(ali_db)
        entrees.append(ali.to_dictionary())

    activites_physiques_db = ActivitePhysiqueDB.query.filter_by(id_patient=id_patient)
    for acti_phy_db in activites_physiques_db:
        acti_phy = ActivitePhysique()
        acti_phy.from_database(acti_phy_db)
        entrees.append(acti_phy.to_dictionary())

    sommeils_db = SommeilDB.query.filter_by(id_patient=id_patient)
    for sommeil_db in sommeils_db:
        som = Sommeil()
        som.from_database(sommeil_db)
        entrees.append(som.to_dictionary())

    masse_db = MasseDB.query.filter_by(id_patient=id_patient)
    for pdb in masse_db:
        masse = Masse()
        masse.from_database(pdb)
        entrees.append(masse.to_dictionary())

    glycemie_db = GlycemieDB.query.filter_by(id_patient=id_patient)
    for gdb in glycemie_db:
        glycemie = Glycemie()
        glycemie.from_database(gdb)
        entrees.append(glycemie.to_dictionary())
    # prêt à l'emploi avec Corpus !
    return entrees


def lire_config(filename: str):
    with open(filename, "r") as f:
        return {line.split(":")[0].strip(): line.split(":")[1].strip() for line in f.readlines()}


# def test_date(dh_test):
#     print(dh_test.nombre_de_jours_separant(dh2))
#     print(dh_test.liste_jours_entre_dates(dh2))
#     print(dh_test.beau_format_heure())
#     print(dh_test.beau_format_jour())
#     print(dh_test.est_anterieur(dh))


def get_taches(patients: List):
    taches = {}
    for patient in patients:
        taches[patient.get_id()] = TacheDB.query.filter_by(patient=patient)
    return taches
