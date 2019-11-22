# SKILVIT

Serveur SKILVIT


## But


## Générer le texte pour l'internationalisation
```bash
pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

pybabel init -i messages.pot -d babel -l de
pybabel init -i messages.pot -d babel -l en
pybabel init -i messages.pot -d babel -l fr

pybabel init -i messages.pot -d babel -l de
pybabel init -i messages.pot -d babel -l en
pybabel init -i messages.pot -d babel -l fr


pybabel compile -d babel
pybabel compile -d babel

pybabel update -i messages.pot -d babel
pybabel update -i messages.pot -d babel

```
