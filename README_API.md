# Intégration frontend / API Go

Le frontend PyQt utilise l’API REST Go configurée par `API_BASE_URL` (par défaut `http://localhost:8080`). Les listes, compteurs, filtres et formulaires chargent les données et envoient les modifications à l’API; les données de démonstration ont été retirées.

## Fonctions reliées

- Connexion et inscription : `POST /auth/login`, `POST /auth/register`; le JWT est envoyé dans les requêtes protégées.
- Professeurs : consultation paginée, professeurs actifs, création, modification et suppression. Les actions de gestion sont réservées aux rôles `ADMIN` et `SUPER_ADMIN`.
- Cours et critères : consultation et opérations CRUD, avec les droits administrateur prévus par l’API.
- Évaluations : soumission par un étudiant avec les identifiants des professeurs, cours et critères chargés en direct. L’année vient du cours sélectionné et l’interface vérifie la fiche d’éligibilité avant d’autoriser la soumission.
- Résultats : consultation par professeur, cours, année et période via `/results/professors/:professor_id`; les options de filtre proviennent des cours et évaluations disponibles. L’année et la période restent modifiables pour interroger les données réellement enregistrées.
- Éligibilité : consultation de la fiche du compte connecté; les administrateurs peuvent créer, modifier et supprimer une fiche à partir de son identifiant étudiant.
- Tableau de bord : effectifs, évaluations récentes et moyenne calculés à partir des réponses de l’API.

## Limites des routes backend actuelles

Le frontend ne peut pas afficher de fonctions que le serveur ne publie pas :

- Il n’existe pas de route de gestion ou de liste des utilisateurs; l’écran Administration l’indique explicitement.
- Un étudiant ne peut pas lister ses propres évaluations : `GET /evaluations` est réservé aux administrateurs.
- Le backend contient un gestionnaire de suppression d’évaluation, mais aucune route `DELETE /evaluations/:id` n’est enregistrée.
- Les fiches d’éligibilité ne peuvent pas être listées en bloc; un administrateur doit saisir l’identifiant de l’étudiant.
- Il n’existe pas de route de modification de profil; l’écran Profil affiche les informations réelles renvoyées à la connexion.

Le compte étudiant de test peut ne pas avoir de fiche d’éligibilité. Dans ce cas, l’API répond `404` et un administrateur doit créer sa fiche avant la soumission.

## Démarrage

Lancer d’abord le serveur Go dans `/home/mulamba-mukoma/Desktop/ProfessorEvaluation` :

```bash
go run cmd/server/main.go
```

Puis lancer l’application depuis ce dossier :

```bash
cd /home/mulamba-mukoma/Desktop/ProfessorEvaluationFrontend/professor_evaluation_frontend
source venv/bin/activate
python main.py
```

Pour utiliser une autre adresse API, définir `API_BASE_URL` dans l’environnement avant de démarrer le frontend.
