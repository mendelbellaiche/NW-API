# NW-API

Projet FastAPI pour la géstion de groupes et de batteries.

## Features

- Authentification
- Création / Lecture / Modification / Suppression de groupes
- Création / Lecture / Modification / Suppression de batteries
- Endpoint supplémentaire de données


## Tech

Technologies utilisé pour ce projet:

- [FastAPI] - Bibliothèque Python pour mettre en place des API Rest
- [SQLAlchemy] - Couche de communication entre FastAPI et la base de données

## Installation

NW-API a besoin de [FastAPI](https://fastapi.tiangolo.com/).

Installation de FastAPI et des dépendances pour le projet.

```sh
pip install virtualenv
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate

pip install fastapi
pip install uvicorn
pip install python-multipart
pip install databases
pip install aiosqlite
```

Pour lancer le projet

```sh
uvicorn run:app --reload
```

## Utilisation

Pour utiliser l'api, cliquez [ici](http://127.0.0.1:8000/docs)

## Authetication

Utilisation de comptes de tests:
- username: johndoe, password: secret
- username: alice, password: secret2

Un cadena à coté de chaque endpoint permet de specifier les crédentials

### Mendel Bellaiche