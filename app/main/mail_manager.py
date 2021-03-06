

import random
from smtplib import SMTPSenderRefused, SMTPRecipientsRefused, SMTPDataError

from flask import render_template
from flask_mail import Message
from flask_babel import lazy_gettext
from app import mail


SENDER = ""


def generer_lien_inscription():
    return random.sample("azertyuiopqsdfghjklmwxcvbn0123456789", 30)


def envoyer_mail_connexion_patient(user):
    msg = Message(lazy_gettext("Nouvelle connexion à votre compte"), sender=SENDER,
                  html=render_template("mails/connexion_patient.html", user=user))
    msg.add_recipient((user.prenom + " " + user.nom, user.email))
    try:
        mail.send(msg)
    except SMTPSenderRefused as e:
        print("Email could not be sent due to refused sender "+user.email)
    except SMTPRecipientsRefused as e:
        print("Email could not be sent due to refused recipient "+user.email)
    except SMTPDataError as e:
        print("Email could not be sent due to data error "+user.email)


def envoyer_mail_connexion_praticien(user):
    msg = Message(lazy_gettext("Nouvelle connexion à votre compte"), sender=SENDER,
                  html=render_template("mails/connexion_praticien.html", user=user))
    msg.add_recipient((user.prenom + " " + user.nom, user.email))
    mail.send(msg)
    try:
        mail.send(msg)
    except SMTPSenderRefused as e:
        print("Email could not be sent due to refused sender "+user.email)
    except SMTPRecipientsRefused as e:
        print("Email could not be sent due to refused recipient "+user.email)
    except SMTPDataError as e:
        print("Email could not be sent due to data error "+user.email)


def envoyer_mail_demande_inscription_patient(user):
    msg = Message(lazy_gettext("Demande de validation de votre inscription"), sender=SENDER,
                  html=render_template("mails/connexion_patient.html", user=user,
                                       link_to_validate="", link_to_dismiss=""))
    msg.add_recipient((user.prenom + " " + user.nom, user.email))
    mail.send(msg)
    try:
        mail.send(msg)
    except SMTPSenderRefused as e:
        print("Email could not be sent due to refused sender "+user.email)
    except SMTPRecipientsRefused as e:
        print("Email could not be sent due to refused recipient "+user.email)
    except SMTPDataError as e:
        print("Email could not be sent due to data error "+user.email)


def envoyer_mail_demande_inscription_praticien(user):
    msg = Message(lazy_gettext("Demande de validation de votre inscription"), sender=SENDER,
                  html=render_template("mails/connexion_praticien.html", user=user,
                                       link_to_validate="", link_to_dismiss=""))
    msg.add_recipient((user.prenom + " " + user.nom, user.email))
    mail.send(msg)
    try:
        mail.send(msg)
    except SMTPSenderRefused as e:
        print("Email could not be sent due to refused sender "+user.email)
    except SMTPRecipientsRefused as e:
        print("Email could not be sent due to refused recipient "+user.email)
    except SMTPDataError as e:
        print("Email could not be sent due to data error "+user.email)


def envoyer_mail_attente_inscirption_praticien(user):
    msg = Message(lazy_gettext("En attente de la validation de votre inscription"), sender=SENDER,
                  html=render_template("mails/attente_validation_praticien.html", user=user))
    msg.add_recipient((user.prenom + " " + user.nom, user.email))
    mail.send(msg)
    try:
        mail.send(msg)
    except SMTPSenderRefused as e:
        print("Email could not be sent due to refused sender "+user.email)
    except SMTPRecipientsRefused as e:
        print("Email could not be sent due to refused recipient "+user.email)
    except SMTPDataError as e:
        print("Email could not be sent due to data error "+user.email)


def envoyer_message_praticien_vers_patient(praticien, patient, sujet, corps):
    msg = Message(subject=sujet, sender=SENDER,
                  html=render_template("mails/message_praticien_vers_patient.html", corps=corps, patient=patient,
                                       praticien=praticien))

    msg.add_recipient((patient.prenom + " " + patient.nom, patient.email))
    mail.send(msg)
    try:
        mail.send(msg)
    except SMTPSenderRefused as e:
        print("Email could not be sent due to refused sender "+praticien.email)
    except SMTPRecipientsRefused as e:
        print("Email could not be sent due to refused recipient "+patient.email)
    except SMTPDataError as e:
        print("Email could not be sent due to data error "+patient.email)
    return True


def envoyer_message_patient_vers_praticien(patient, praticien, sujet, corps):
    msg = Message(subject=sujet, sender=SENDER,
                  html=render_template("mails/message_patient_vers_praticien.html", corps=corps, patient=patient,
                                       praticien=praticien))

    msg.add_recipient((patient.prenom + " " + patient.nom, patient.email))
    mail.send(msg)
    try:
        mail.send(msg)
    except SMTPSenderRefused as e:
        print("Email could not be sent due to refused sender "+patient.email)
    except SMTPRecipientsRefused as e:
        print("Email could not be sent due to refused recipient "+patient.email)
    except SMTPDataError as e:
        print("Email could not be sent due to data error "+patient.email)
    return True


def envoyer_message_contact(email_address: str, content: str, language="fr"):
    # Send to contact
    msg1 = Message(subject=lazy_gettext("Message envoyé à Skilvit"), sender=SENDER,
                   html=render_template("mails/message_contact.html", corps=content))
    msg1.add_recipient((email_address, email_address))
    mail.send(msg1)

    # Send to admin of the website
    msg2 = Message(subject=lazy_gettext("Message reçu d'un curieux"), sender=SENDER,
                   html=render_template("mails/message_contact_admin.html", destinataire=email_address, corps=content))
    msg2.add_recipient((SENDER, SENDER))
    mail.send(msg2)
    return True
