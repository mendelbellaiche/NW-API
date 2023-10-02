# NW-API

Projet FastAPI pour la géstion de groupes et de batteries.

## Features

- Authentification
- Création / Lecture / Modification / Suppression de groupes
- Création / Lecture / Modification / Suppression de batteries
- Entrypoint supplémentaire de données


## Tech

Technologies utilisé pour ce projet:

- [FastAPI] - Bibliothèque Python pour mettre en place des API Rest
- [SQLAlchemy] - Couche de communication entre FastAPI et la base de données

## Installation

NW-API a besoin de [FastAPI](https://fastapi.tiangolo.com/).

Installation de FastAPI et des dépendances pour le projet.

```sh
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

### Mendel Bellaiche