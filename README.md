# CMU Manager

Application web Django de gestion des cartes CMU.

## Présentation

CMU Manager est une application web professionnelle permettant de gérer la recherche, l’importation, l’exportation et l’administration des données des cartes CMU.

L’objectif principal est d’aider les opérateurs à retrouver rapidement un client et à identifier son **code rangement**, qui est l’information essentielle pour récupérer la carte physique.

---

## Fonctionnalités principales

### Authentification et sécurité
- connexion / déconnexion,
- gestion des rôles,
- comptes bannis,
- changement de mot de passe,
- réinitialisation de mot de passe par l’administration.

### Rôles utilisateurs
- **Super administrateur**
- **Administrateur**
- **Opérateur**

### Gestion des clients
- recherche rapide par :
  - noms,
  - prénoms,
  - contact,
  - date de naissance,
- affichage clair des résultats,
- mise en avant visuelle du code rangement,
- consultation du détail client.

### Import de données
- import CSV,
- import Excel (.xlsx),
- validation des colonnes,
- conversion des dates,
- détection des doublons,
- confirmation avant mise à jour,
- historique des imports.

### Export
- export CSV,
- export Excel,
- export global ou filtré.

### Gestion des utilisateurs
- création de comptes,
- attribution de rôles par le super administrateur,
- bannissement,
- réactivation,
- suppression,
- réinitialisation du mot de passe.

### Administration avancée
- admin Django personnalisé,
- accès réservé au super administrateur,
- pages d’erreur personnalisées,
- vidage des données métier.

---

## Stack technique

- Python
- Django
- Django Templates
- Bootstrap 5
- SQLite
- Pandas
- OpenPyXL
- HTMX (pour certaines interactions dynamiques)

---

## Structure du projet

```bash
cmu_manager/
├── apps/
│   ├── accounts/
│   ├── clients/
│   ├── imports/
│   ├── dashboard/
│   └── common/
├── config/
├── static/
├── templates/
├── manage.py
├── requirements.txt
└── README.md