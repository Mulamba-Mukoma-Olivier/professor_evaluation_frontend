# Professor Evaluation Frontend - Intégration Complète API Go & PyQt5

Ce projet constitue le frontend de bureau (PyQt5) connecté à l'API REST développée en Go (`/home/mulamba-mukoma/Desktop/ProfessorEvaluation`).

---

## 1. Structure du projet

```
ProfessorEvaluationFrontend/
├── api/                       # Couche Client API REST (communication HTTP avec le backend Go)
│   ├── client.py             # Client HTTP avec gestion du token JWT et requêtes sécurisées
│   ├── auth_api.py           # Authentification : /auth/login et /auth/register
│   ├── professors_api.py     # CRUD Professeurs : /professors, /professors/active, /professors/by-status
│   ├── courses_api.py        # CRUD Cours : /courses, /courses/:id
│   ├── criteria_api.py       # CRUD Critères : /criteria, /criteria/active, /criteria/:id
│   ├── evaluations_api.py    # Soumission et consultation des évaluations : /evaluations
│   ├── results_api.py        # Consultation des moyennes et résultats : /results/professors/:id
│   └── eligibility_api.py    # Vérification et gestion d'éligibilité : /eligibility/:student_id
├── logic/                     # Couche Métier et Contrôleurs PyQt5
│   ├── login_logic.py        # Fenêtre de connexion avec validation et lien d'inscription
│   ├── signup_logic.py       # Formulaire d'inscription (rôles STUDENT, PROFESSOR, ADMIN)
│   ├── main_section_logic.py # Contrôleur principal des 7 pages natives de ui/main_section.ui
│   ├── dialogs.py            # Modales d'ajout/édition (Professeur, Cours, Critère, Éligibilité)
│   ├── admin_profile_logic.py# Profil et supervision administrateur
│   ├── user_profile_logic.py # Profil et préférences utilisateur
│   ├── professors_logic.py   # Wrapper rétrocompatible pour professeurs
│   ├── courses_logic.py      # Wrapper rétrocompatible pour cours
│   ├── criteria_logic.py     # Wrapper rétrocompatible pour critères
│   ├── evaluations_logic.py  # Wrapper rétrocompatible pour évaluations
│   ├── results_logic.py      # Wrapper rétrocompatible pour résultats
│   └── eligibility_logic.py  # Wrapper rétrocompatible pour éligibilités
├── ui/                        # Fichiers d'interface graphique (Qt Designer)
│   ├── login.ui              # Écran de connexion
│   ├── signup.ui             # Écran d'inscription
│   ├── main_section.ui       # Fenêtre principale (7 pages natives)
│   ├── admin_profile.ui      # Modale profil administrateur
│   └── user_profile.ui       # Modale profil utilisateur
├── config.py                 # Configuration globale (URL API, chemins UI)
├── requirements.txt          # Dépendances Python (PyQt5, requests, etc.)
└── main.py                   # Point d'entrée de l'application
```

---

## 2. Correspondance des 7 Pages de l'Interface Principale

L'interface principale (`ui/main_section.ui`) contient un `QStackedWidget` avec 7 pages natives conçues pour refléter le métier de l'API Go :

| Index | Nom dans le UI | Titre / Rôle | Fonctionnalités intégrées avec l'API Go |
|---|---|---|---|
| **0** | `page` | **Dashboard / Accueil** | • Compteurs en temps réel : Professeurs, Cours, Évaluations, Critères<br>• Liste dynamique des évaluations récentes soumises (`QListView`)<br>• Salutation personnalisée avec le rôle de l'utilisateur connecté |
| **1** | `page_2` | **Professeurs** | • `QTableView` paginé (Matricule, Nom, Email, Département, Grade, Statut)<br>• Recherche en temps réel (`lineEdit`)<br>• Bouton `+ Ajouter un professeur` (ouvre `ProfessorDialog`)<br>• Clic droit / Double-clic : Modifier / Supprimer / Voir les résultats |
| **2** | `page_3` | **Cours** | • `QTableView` paginé (Code, Nom, Département, Année, Description)<br>• Recherche en temps réel (`lineEdit_2`)<br>• Bouton `+ Ajouter un cours` (ouvre `CourseDialog`)<br>• Clic droit / Double-clic : Modifier / Supprimer |
| **3** | `page_4` | **Critères** | • `QTableView` des critères d'évaluation actifs et inactifs<br>• Recherche en temps réel (`lineEdit_3`)<br>• Bouton `+ Ajouter un critère` (ouvre `CriterionDialog`)<br>• Clic droit / Double-clic : Modifier / Supprimer |
| **4** | `page_5` | **Éligibilités** | • Vérification du statut de l'étudiant connecté (`/eligibility/:student_id`)<br>• Indicateurs visuels pour Inscription, Frais académiques, Frais labo, Frais d'accès<br>• Badge de statut Vert/Rouge avec motifs de non-éligibilité détaillés<br>• Outil administrateur pour consulter et régulariser l'éligibilité d'un étudiant |
| **5** | `page_6` | **Évaluations** | • Liste déroulante des professeurs actifs (`/professors/active`)<br>• Liste déroulante des cours disponibles (`/courses`)<br>• 10 groupes indépendants de boutons radio (notes de 1 à 5)<br>• Bouton `Évaluer` connecté à `POST /evaluations`<br>• Contrôle des droits (réservé aux étudiants) et gestion des doublons |
| **6** | `page_7` | **Résultats** | • Sélection dynamique du professeur (`comboBox_3`)<br>• Barre de progression et affichage de la note globale moyenne (`/results/professors/:id`)<br>• Nombre total d'avis enregistrés<br>• 10 champs dédiés affichant la moyenne détaillée par critère |

---

## 3. Comptes de Test Disponibles

Plusieurs comptes sont pré-configurés dans la base de données SQLite du backend (`professor_evaluation.db`) :

| Rôle | Email | Mot de passe | Description |
|---|---|---|---|
| **ADMIN** | `admin@example.com` | `adminpassword123` | Compte administrateur complet (accès CRUD, dashboard, supervision) |
| **STUDENT** | `e2e+test@example.com` | `secret123` | Compte étudiant (éligible, peut soumettre des évaluations) |

> **Note :** Vous pouvez également créer à tout moment un nouveau compte depuis le bouton **"S'inscrire"** de l'écran de connexion. Le mot de passe doit comporter **au moins 8 caractères** conformément aux règles de l'API Go.

---

## 4. Démarrage de l'Application

### 1. Démarrer le Backend Go (si non démarré) :
```bash
cd /home/mulamba-mukoma/Desktop/ProfessorEvaluation
go run cmd/server/main.go
```
*Le serveur s'exécute sur `http://localhost:8080`.*

### 2. Démarrer le Frontend PyQt5 :
```bash
cd /home/mulamba-mukoma/Desktop/ProfessorEvaluationFrontend
source venv/bin/activate
python3 main.py
```
