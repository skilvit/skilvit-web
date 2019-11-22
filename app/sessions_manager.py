# -*-coding:utf-8-*-

# from PyQt5.QtGui.QRawFont import glyphIndexesForString
import time

from app.database_manager import *
from app.utils import *
from app import data_manager as dm
from datetime import datetime, date
from sqlalchemy import tuple_

__author__ = "Clément Besnier <skilvitapp@gmail.com>"


engine = db.create_engine('sqlite:///sqlalchemy_example.db')
DBSession = db.sessionmaker(bind=engine)
db_session = DBSession()


class Utilisateur:
    def __init__(self, pseudo):
        self.pseudo = pseudo

    @staticmethod
    def creer_nouveau(forme, mdp_hash):
        raise NotImplementedError


class Patients:
    def __init__(self):
        self.chemin = os.path.join("static", "patients")
        self.fichier = "liste_patients.txt"
        self.identifiants_patients = []

    def charger_patients(self):
        """
        Charge l'ensemble des identifiants des patients
        :return:
        """
        with open(os.path.join(self.chemin, self.fichier), "r") as f:
            self.identifiants_patients = f.read().split("\n")

    def id_patient_existe(self, id_patient):
        if self.identifiants_patients is not None:
            return id_patient in self.identifiants_patients
        else:
            return False

    @staticmethod
    def retrieve_patient_by_validation_link(link):
        return dm.PatientDB.query.filter_by(link_to_validate=link).first()

    @staticmethod
    def validate_patient(patient):
        patient.link_to_validate = ""
        patient.confirmed = True
        patient.confirmed_on = datetime.datetime.now()
        db.session.commit()

    @staticmethod
    def check_if_patient_exists_by_email_address(email_address):
        return PatientDB.query.filter_by(email=email_address).first()


class Praticiens:
    def __init__(self):
        self.chemin = os.path.join("static", "praticiens")
        self.fichier = "liste_praticients.txt"
        self.identifiants_praticiens = None

    def charger_praticiens(self):
        with open(os.path.join(self.chemin, self.fichier), "r") as f:
            self.identifiants_praticiens = f.read().split("\n")

    def id_praticien_existe(self, id_praticien):
        if self.identifiants_praticiens is not None:
            return id_praticien in self.identifiants_praticiens
        else:
            return False

    def supprimer_praticien(self):
        """
        Si un praticien cesse de vouloir continuer l'application
        :return:
        """
        # TODO suppression d'un praticien
        pass

    @staticmethod
    def retrieve_praticien_by_validation_link(link):
        return dm.PraticienDB.query.filter_by(link_to_validate=link).first()

    @staticmethod
    def validate_praticien(praticien):
        praticien.link_to_validate = ""
        praticien.confirmed = True
        praticien.confirmed_on = datetime.datetime.now()
        db.session.commit()


class PatientSess(Utilisateur):
    """
    Gère à la fois le patient pour la session que pour la db
    """

    def __init__(self, pseudo):
        Utilisateur.__init__(self, pseudo)
        self.chemin_fichiers = os.path.join("static", "patients")
        self.nom_fichier = pseudo
        # print(PatientDB.query.all())
        self.patient_db = PatientDB.query.filter_by(email=pseudo).first()
        # print(self.patient_db)
        # if self.patient_db is None:
        #     nouveau_patient = PatientDB(prenom="Clément", nom="BESNIER", sexe=Sexe.homme,
        #                                 date_naissance=datetime.date(1994, 3, 1), email="clemsciences",
        #                                 date_inscription=datetime.date(2017, 12, 17),
        #                                 mdp="clemsciences", )
        #     db_session.add(nouveau_patient)
        #     db_session.commit()
        #     self.patient_db = nouveau_patient

    @staticmethod
    def creer_nouveau(forme, mdp_hash):
        # TODO normaliser les données
        print("tout", PatientDB.query.all())
        date_naissance = datetime.strptime(forme["jour_"]+"/"+forme["mois_"]+"/"+forme["annee_"], "%d/%m/%Y")
        nouveau_patient = PatientDB(prenom=forme["first_name"], nom=forme["family_name"],
                                    sexe=Sexe[forme["sex"]],
                                    date_naissance=date_naissance,
                                    email=forme["email_address"], mdp_hash=mdp_hash,
                                    date_inscription=datetime.now())
        print("new", nouveau_patient)
        # nouveau_patient = PatientDB(prenom=forme.prenom.data, nom=forme.nom.data,
        #                             sexe=Sexe[forme.sexe.data],
        #                             date_naissance=dm.Date.from_html_to_date(forme.date_naissance.data),
        #                             email=forme.email.data, mdp_hash=forme.mdp_patient.data,
        #                             date_inscription=datetime.datetime.now())

        dm.db.session.add(nouveau_patient)
        dm.db.session.commit()
        # try:
        #     dm.db.session.commit()
        # except:
        #     dm.db.session.rollback()
        return nouveau_patient

    @staticmethod
    def consulter_pseudo_patient(pseudo):
        print(PatientDB.query.all())
        patient_db = PatientDB.query.filter_by(email=pseudo).first()
        if patient_db is not None:
            return patient_db.mdp
        else:
            return ""

    def de_dictionnaire(self, d):
        pass

    def en_dictionnaire(self):
        # d = {}
        pass

    def acceder_praticiens(self):
        relations = RelationPatientPraticienDB.query.filter_by(id_patient=self.patient_db.get_id(),
                                                               actif=True).order_by(
            RelationPatientPraticienDB.date_heure_debut).all()
        return [relation.praticien for relation in relations]

    def voir_si_ajouter_praticien(self, email_praticien):
        """
        Inutile en fait
        :param email_praticien:
        :return:
        """
        praticien_db = PraticienDB.query.filter_by(email=email_praticien).first()
        if praticien_db is None:
            return None
        demande = DemandeConnexionPatientPraticienDB(id_patient=self.patient_db.get_id(),
                                                     id_praticien=praticien_db.get_id(),
                                                     date_heure_demande=datetime.now())
        dm.db.session.add(demande)
        dm.db.session.commit()
        return True

    def definir_praticien(self, email_praticien):
        praticien_db = PraticienDB.query.filter_by(email=email_praticien).first()
        if praticien_db is None:
            return None
        demande = DemandeConnexionPatientPraticienDB(id_patient=self.patient_db.get_id(),
                                                     id_praticien=praticien_db.get_id(),
                                                     date_heure_demande=datetime.now())
        print(demande)
        dm.db.session.add(demande)
        dm.db.session.commit()
        return praticien_db

    def supprimer_compte(self):
        """
        Supprime le compte utilisateur de ce patient
        :return:
        """
        pass

    def to_json(self):
        id_patient = self.patient_db.get_id()
        return dm.get_entrees_patient(id_patient)

    def to_txt(self):
        entrees = self.to_json()
        lignes = []

        for entree in entrees:
            lignes.append("\n"+entree["type"])
            lignes.append("".join(["\n".join(["\t"+champ+" : "+str(entree[champ])
                                              for champ in entree if entree[champ] is not None])]))
        return lignes

    # def to_pdf(self):
    #     entrees = self.to_json()

    def to_csv(self):
        entrees = self.to_json()
        clefs = set(["\t".join(entree) for entree in entrees])
        lignes = []
        print("clefs", clefs)
        for clef in clefs:
            lignes.append([])
            lignes.append(clef.split("\t"))
            for entree in entrees:
                if clef == "\t".join(entree.keys()):
                    ligne = [str(entree[champ]) for champ in clef.split("\t")]
                    print("ligne fabrication", ligne)
                    lignes.append(ligne)
        return lignes

    def enregistrer_entree_situation(self, situation):
        situation_db = SituationDB(id_patient=self.patient_db.get_id(), date_heure=situation.date_heure,
                                   situation=situation.situation,
                                   intensite=situation.intensite,
                                   emotions_sensations=situation.emotions_sensations,
                                   comportement=situation.comportement,
                                   pensees=situation.pensees,
                                   taux_croyance=situation.taux_croyance,
                                   pensee_alternative=situation.pensee_alternative,
                                   taux_croyance_actualise=situation.taux_croyance_actualise)
        dm.db.session.add(situation_db)
        dm.db.session.commit()

    def enregistrer_entree_repas(self, alimentation):
        alimentation_db = AlimentationDB(id_patient=self.patient_db.get_id(),
                                         date_heure=alimentation.date_heure,
                                         repas=alimentation.repas,
                                         nourriture=alimentation.nourriture)
        dm.db.session.add(alimentation_db)
        dm.db.session.commit()

    def enregistrer_entree_prise_medicament(self, prise_medicament):
        pr_mr_db = PriseMedicamentDB(id_patient=self.patient_db.get_id(),
                                     date_heure=prise_medicament.date_heure,
                                     medicament=prise_medicament.medicament,
                                     dosage=prise_medicament.dosage)
        dm.db.session.add(pr_mr_db)
        dm.db.session.commit()

    def enregistrer_entree_sommeil(self, sommeil):
        somm_db = SommeilDB(id_patient=self.patient_db.get_id(), date_heure=sommeil.date_heure,
                            date_heure_evenement=sommeil.date_heure_evenement,
                            evenement=sommeil.evenement, commentaire=sommeil.commentaire)
        dm.db.session.add(somm_db)
        dm.db.session.commit()

    def enregistrer_entree_activite_physique(self, activite_physique):
        acti_db = ActivitePhysiqueDB(id_patient=self.patient_db.get_id(),
                                     date_heure=activite_physique.date_heure,
                                     duree=activite_physique.duree,
                                     sport=activite_physique.sport,
                                     difficulte_ressentie=activite_physique.difficulte_ressentie)
        dm.db.session.add(acti_db)
        dm.db.session.commit()

    def enregistrer_glycemie(self, glycemie):
        gl_db = GlycemieDB(id_patient=self.patient_db.get_id(),
                           glycemie=glycemie.glycemie,
                           date_heure=glycemie.date_heure)
        dm.db.session.add(gl_db)
        dm.db.session.commit()

    def enregistrer_poids(self, poids):
        ps_db = PoidsDB(id_patient=self.patient_db.get_id(),
                        poids=poids.poids,
                        date_heure=poids.date_heure)
        dm.db.session.add(ps_db)
        dm.db.session.commit()

    def obtenir_entrees_etat(self):
        situations = []
        for situation_db in SituationDB.query.filter_by(id_patient=self.patient_db.get_id()):
            situation = dm.Situation()
            situation.from_database(situation_db)
            situations.append(situation)
        return situations

    def obtenir_entrees_repas(self, ):
        repas = []
        for alimentation_db in AlimentationDB.query.filter_by(id_patient=self.patient_db.get_id()):
            alimentation = dm.Alimentation()
            alimentation.from_database(alimentation_db)
            repas.append(alimentation)
        return repas

    def obtenir_entrees_prise_medicament(self):
        pms = []
        for pm_db in PriseMedicamentDB.query.filter_by(id_patient=self.patient_db.get_id()):
            pm = dm.PriseMedicament()
            pm.from_database(pm_db)
            pms.append(pm)
        return pms

    def obtenir_entrees_sommeil(self):
        sommeils = []
        for sommeil_db in SommeilDB.query.filter_by(id_patient=self.patient_db.get_id()):
            sommeil = dm.Sommeil()
            sommeil.from_database(sommeil_db)
            sommeils.append(sommeil)
        return sommeils

    def obtenir_entrees_activite_physique(self):
        activites_physiques = []
        for activite_physique_db in ActivitePhysiqueDB.query.filter_by(id_patient=self.patient_db.get_id()):
            activite_physique = dm.ActivitePhysique()
            activite_physique.from_database(activite_physique_db)
            activites_physiques.append(activite_physique)
        return activites_physiques

    def obtenir_entrees_poids(self):
        l_poids = []
        for poids_db in PoidsDB.query.filter_by(id_patient=self.patient_db.get_id()):
            poids = dm.Poids()
            poids.from_database(poids_db)
            l_poids.append(poids)
        return l_poids

    def obtenir_entrees_glycemie(self):
        glycemies = []
        for glycemie_db in GlycemieDB.query.filter_by(id_patient=self.patient_db.get_id()):
            glycemie = dm.Glycemie()
            glycemie.from_database(glycemie_db)
            glycemies.append(glycemie)
        return glycemies

    def tout_obtenir(self):
        enregistrements = []
        enregistrements.extend(self.obtenir_entrees_etat())
        enregistrements.extend(self.obtenir_entrees_prise_medicament())
        enregistrements.extend(self.obtenir_entrees_repas())
        enregistrements.extend(self.obtenir_entrees_sommeil())
        enregistrements.extend(self.obtenir_entrees_glycemie())
        enregistrements.extend(self.obtenir_entrees_activite_physique())
        enregistrements.extend(self.obtenir_entrees_poids())
        return enregistrements

    @staticmethod
    def obtenir_praticien(praticien_id):
        return dm.PraticienDB.query.filter_by(_id=praticien_id).first()

    # region anamnèse côté patient
    def ajouter_anamnese_patient(self, patient_id, texte, categorie):
        anamnese = dm.Anamnese(id_patient=patient_id, categorie=categorie, contenu=texte)
        dm.db.session.add(anamnese)
        dm.db.session.commit()
        return anamnese

    def supprimer_anamnese_patient(self, patient_id, id_anamnese):
        dm.Anamnese.query.filter_by(id_patient=patient_id, id=id_anamnese).delete()
        dm.db.session.commit()

    def mettre_a_jour_anamnese_patient(self, patient_id, id_anamnese, nouveau_texte):
        anamnese = dm.Anamnese.query.filter_by(id_patient=patient_id, id=id_anamnese).first()
        anamnese.contenu = nouveau_texte
        dm.db.session.commit()

    def lire_anamnese_patient(self, patient_id):
        anamneses = dm.Anamnese.query.filter_by(id_patient=patient_id).order_by(dm.Anamnese.date_creation).all()
        return {categorie: [anamnese for anamnese in anamneses if anamnese.categorie == categorie]
                for categorie in dm.Anamnese.categories}
    # endregion


class PraticienSess(Utilisateur):
    def __init__(self, pseudo):
        Utilisateur.__init__(self, pseudo)
        self.chemin_fichiers = os.path.join("static", "praticiens")
        self.nom_fichier = pseudo
        self.praticien_db = PraticienDB.query.filter_by(email=pseudo).first()

    @staticmethod
    def nouvelle_inscription_praticien(forme):
        print(os.getcwd())
        print(os.path.join(DIRECTORY_JSON, "nouveau_praticien_" + str(datetime.now().ctime())) + ".json")
        with open(os.path.join(os.getcwd(), DIRECTORY_JSON, "nouveau_praticien_" + str(time.time())) + ".json",
                  "w") as f:
            json.dump(forme, f)

    @staticmethod
    def creer_nouveau(forme, mdp_hash):
        # TODO normaliser les données
        print(PraticienDB.query.all())
        nouveau_praticien = PraticienDB(prenom=forme["first_name"], nom=forme["family_name"],
                                        numero_telephone=forme["phone_number"],
                                        profession=forme["job"], rue=forme["street"], code_postal=forme["post_code"],
                                        ville=forme["city"], pays=forme["country"],
                                        email=forme["email_address"], mdp_hash=mdp_hash,
                                        date_inscription=datetime.now())
        dm.db.session.add(nouveau_praticien)
        try:
            dm.db.session.commit()
        except:
            dm.db.session.rollback()
        return nouveau_praticien

    @staticmethod
    def consulter_pseudo_praticien(pseudo):
        """

        :param pseudo:
        :return: mot de passe si le pseudo existe, "" sinon
        """
        print(PraticienDB.query.all())
        praticien_db = PraticienDB.query.filter_by(email=pseudo).first()
        if praticien_db is not None:
            return praticien_db.mdp
        else:
            return ""

    def acceder_patient(self, index):
        relation = RelationPatientPraticienDB.query.filter_by(praticien=self.praticien_db,
                                                              actif=True, id_patient=index).first()
        if relation:
            return relation.patient
        else:
            return None

    def acceder_patients(self):
        relations = RelationPatientPraticienDB.query.filter_by(praticien=self.praticien_db, actif=True).all()
        # print(relations)
        # print([relation.patient for relation in relations])
        return [relation.patient for relation in relations]

    def acceder_nouveaux_patients(self):
        print("acces")
        print(DemandeConnexionPatientPraticienDB.query.all())
        demandes = DemandeConnexionPatientPraticienDB.query.filter_by(praticien=self.praticien_db,
                                                                      repondu=False).order_by(
            DemandeConnexionPatientPraticienDB.date_heure_demande).all()
        print(demandes)
        return [demande.patient for demande in demandes]

    def ajouter_patient(self, email_patient):
        patient = PatientDB.query.filter_by(email=email_patient).first()
        relation = RelationPatientPraticienDB(id_patient=patient.get_id(), patient=patient, praticien=self.praticien_db,
                                              id_praticien=self.praticien_db.get_id(),
                                              date_heure_debut=datetime.now(), actif=True)
        demande = DemandeConnexionPatientPraticienDB.query.filter_by(praticien=self.praticien_db,
                                                                     patient=patient).first()
        demande.repondu = True

        dm.db.session.add(relation)
        dm.db.session.commit()
        return patient

    def supprimer_patient(self, patient_id):
        """
        Supprimer le lien entre le praticien et le patient
        :return:
        """
        RelationPatientPraticienDB.query.filter_by(id_patient=patient_id,
                                                   id_praticien=self.praticien_db.id_praticien).delete()
        dm.db.session.commit()

    def creer_questionnaire(self, contenu):
        questionnaire = dm.QuestionnaireDB(praticien=self.praticien_db, date_creation=date.today(),
                                           contenu=contenu)
        dm.db.session.add(questionnaire)
        dm.db.session.commit()

    def recuperer_questionnaires(self):
        return QuestionnaireDB.query.filter_by(praticien=self.praticien_db)

    def voir_entrees_patient(self, patient_id):
        if(len(RelationPatientPraticienDB.query.filter_by(
                praticien=self.praticien_db, id_patient=patient_id, actif=True).all()) == 1):
            return dm.get_entrees_patient(patient_id)

    def ajouter_tache_patient(self, patient_id, tache):
        nouvelle_tache = dm.TacheDB(praticien=self.praticien_db, id_patient=patient_id,
                                    date_creation=datetime.datetime.now(), contenu=tache)
        dm.db.session.add(nouvelle_tache)
        dm.db.session.commit()

    @staticmethod
    def get_patient(index):
        return dm.PatientDB.query.filter_by(_id=index).first()
        # for patient in dm.PatientDB.query.all():
        #     print(patient._id)
        # print(dm.PatientDB.query.filter_by(_id=index).all())
        # relation = RelationPatientPraticienDB.query.filter_by(patient=index, praticien=self.praticien_db,
        #                                            actif=True).first()
        # print(relation)
        # if True:
        # else:
        #     return -1

    def ajouter_commentaire_sur_entree_patient(self, entry_id, tablename, text, patient_id):
        commentaire = dm.AnnotationEntree(id_entree=entry_id, tablename=tablename, praticien=self.praticien_db,
                                          annotation=text, id_patient=patient_id)
        dm.db.session.add(commentaire)
        dm.db.session.commit()
        return commentaire.get_id()

    def voir_commentaires(self, patient_id):
        commentaires = dm.AnnotationEntree.query.filter_by(praticien=self.praticien_db, id_patient=patient_id)
        return commentaires

    def supprimer_commentaires_sur_entree_patient(self, patient_id, commentaire_a_supprimer):
        dm.AnnotationEntree.query.filter_by(_id=commentaire_a_supprimer, id_patient=patient_id,
                                            id_praticien=self.praticien_db.get_id()).delete()
        # dm.db.session.delete(commentaire)
        dm.db.session.commit()

    @staticmethod
    def charger_commentaire_sur_entree_patient(patient_id, commentaires_voulus):
        # commentaires_voulus : [("nom de la table", numéro de l'entrée)]
        rs = []
        for commentaires in commentaires_voulus:
            machin = dm.AnnotationEntree.query.filter_by(tablename=commentaires[0], id_entree=commentaires[1],
                                                         id_patient=patient_id).all()
            if machin:
                rs.extend(machin)

        return rs
        # return dm.AnnotationEntree.query.filter(
        #     tuple_(dm.AnnotationEntree.tablename, dm.AnnotationEntree.id_entree
        #            ).in_(commentaires_voulus)).filter_by(id_patient=patient_id).all()
        # dm.AnnotationEntree.patient.
        # from sqlalchemy import tuple_
        # session.query(Record).filter(tuple_(Record.id1, Record.id2).in_(seq)).all()

    def ajouter_fiche_seance(self, index, contenu, date_heure):
        nouvelle_fiche_seance = dm.SuiviPatient(contenu=contenu, date_heure=date_heure, id_patient=index,
                                                id_praticien=self.praticien_db.get_id())
        dm.db.session.add(nouvelle_fiche_seance)
        dm.db.session.commit()
        return nouvelle_fiche_seance

    def afficher_fiches_seances(self, index):
        fiches_seances = dm.SuiviPatient.query.filter_by(id_patient=index,
                                                         id_praticien=self.praticien_db.get_id()).all()
        # l = []
        # for fiche in fiches_seances:
        #     date_heure = dm.DateHeure()
        #     date_heure.from_datetime(fiche.date_heure)
        #     fiche.date_heure = date_heure
        #     l.append(fiche)
        # return l
        return fiches_seances

    def supprimer_fiche_seance(self, patient_id, fiche_id):
        dm.SuiviPatient.query.filter_by(_id=fiche_id, id_patient=patient_id,
                                        id_praticien=self.praticien_db.get_id()).delete()
        # dm.db.session.delete(commentaire)
        dm.db.session.commit()

    def modifier_fiche_seance(self, patient_id, fiche_id, texte):
        fiche = dm.SuiviPatient.query.filter_by(_id=fiche_id, id_patient=patient_id,
                                                id_praticien=self.praticien_db.get_id()).first()
        fiche.contenu = texte
        dm.db.session.commit()

    def lire_anamnese_patient(self, patient_id):
        anamneses = dm.Anamnese.query.filter_by(id_patient=patient_id).order_by(dm.Anamnese.date_creation).all()
        return {categorie: [anamnese for anamnese in anamneses if anamnese.categorie == categorie]
                for categorie in dm.Anamnese.categories}


def consulter_pseudo(pseudo):
    """
    Gestion des sessions
    :param pseudo:
    :return:
    """
    if pseudo in pseudo_mdp:
        return pseudo_mdp[pseudo]
    else:
        return ""


def consulter_pseudo_patient(pseudo):
    if pseudo in pseudo_patients_mdp:
        return pseudo_patients_mdp[pseudo]
    else:
        return ""
