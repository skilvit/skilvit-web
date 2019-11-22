

__author__ = "Clément Besnier <skilvitapp@gmail.com>"

URL = ""  # TODO define it

EMAIL_PATTERN = r"^[A-Za-z0-9\-_\.]+@[A-Za-z0-9\-_\.]+\.[a-z]{2,4}"

champs = ["Entree", "prise_medicament"]
champs_entrees = ["type", "jour", "mois", "annee", "heure", "minute", "intensite", "situation", "emotions_sensations", "pensees", "taux_croyance", "pensee_alternative","taux_croyance_actualise", "comportement"]
champs_entrees_pour_tableau = ["type", "date", "heure", "intensite", "situation", "emotions_sensations", "pensees", "taux_croyance", "pensee_alternative","taux_croyance_actualise", "comportement"]
champs_entrees_pour_tableau_affichage = ["type", "date", "heure", "intensité", "situation", "émotions et sensations", "pensées", "taux de croyance", "pensée alternative","taux de croyance actualisé", "comportement"]
champs_prise_medicament = ["type", "jour", "mois", "annee", "heure", "minute", "medicament", "dosage"]
champs_prise_pour_tableau = ["type", "date", "heure", "medicament", "dosage"]
champs_prise_pour_tableau_affichage = ["type", "date", "heure", "médicament", "dosage"]

alphabet_code = "azertyuiopqsdfghjklmwxcvbn"
