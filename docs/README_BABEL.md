

```bash
# Générer le messages.pot
pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot app


# création du dossier babel avec les traductions selon les langues (à refaire sur chaque ordi et si on change de dossier)
pybabel init -i messages.pot -d app/translations -l fr
pybabel init -i messages.pot -d app/translations -l en
pybabel init -i messages.pot -d app/translations -l de

# On traduit le texte
# On compile les .po en .mo (le plus important à faire quand on fait une traduction)
pybabel compile -d app/translations
 
# On met à jour les .po en fonction  du .pot (utile que quand on rajoute des mots à traduire)
pybabel update -i messages.pot -d app/translations

```