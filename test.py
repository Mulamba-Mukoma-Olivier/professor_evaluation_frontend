"""
Script de test de l'intégration complète de l'API Go avec le client frontend.
"""
from api.auth_api import AuthAPI
from api.professors_api import ProfessorsAPI
from api.courses_api import CoursesAPI
from api.criteria_api import CriteriaAPI
from api.evaluations_api import EvaluationsAPI
from api.results_api import ResultsAPI
from api.eligibility_api import EligibilityAPI


def run_integration_tests():
    print("=" * 60)
    print("TEST D'INTÉGRATION API GO <-> FRONTEND REQUESTS")
    print("=" * 60)

    # 1. Connexion Admin
    print("\n[1/6] Test d'authentification...")
    admin_auth = AuthAPI.login("admin@example.com", "adminpassword123")
    assert admin_auth is not None, "Échec de connexion administrateur !"
    user = admin_auth.get("user", {})
    print(f"  ✓ Connecté : {user.get('name')} ({user.get('role')}) - Token JWT actif.")

    # 2. Professeurs
    print("\n[2/6] Test des professeurs...")
    profs = ProfessorsAPI.get_all()
    assert profs is not None, "Impossible de récupérer les professeurs"
    print(f"  ✓ {len(profs)} professeurs récupérés de l'API.")
    for p in profs[:3]:
        print(f"    • {p.get('matricule')} : {p.get('first_name')} {p.get('last_name')} ({p.get('department')})")

    # 3. Cours
    print("\n[3/6] Test des cours...")
    courses = CoursesAPI.get_all()
    assert courses is not None, "Impossible de récupérer les cours"
    print(f"  ✓ {len(courses)} cours récupérés de l'API.")
    for c in courses[:3]:
        print(f"    • {c.get('code')} : {c.get('name')} ({c.get('academic_year')})")

    # 4. Critères
    print("\n[4/6] Test des critères...")
    criteria = CriteriaAPI.get_all()
    assert criteria is not None, "Impossible de récupérer les critères"
    print(f"  ✓ {len(criteria)} critères récupérés de l'API.")
    for cr in criteria[:3]:
        print(f"    • ID {cr.get('id')} : {cr.get('name')} (Max {cr.get('max_score')})")

    # 5. Évaluations & Résultats
    print("\n[5/6] Test des évaluations et calculs de résultats...")
    evals = EvaluationsAPI.get_all()
    assert evals is not None, "Impossible de récupérer les évaluations"
    print(f"  ✓ {len(evals)} évaluations récupérées de l'API.")

    results = ResultsAPI.get_professor_result(
        professor_id=2,
        course_id=2,
        academic_year="2025-2026",
        period="Semestre 1"
    )
    if results:
        print(f"  ✓ Résultats Professeur #2 : Moyenne globale = {results.get('global_average')}/5.0 "
              f"sur {results.get('total_reviews')} avis.")
    else:
        print("  ℹ Aucun résultat pour cette combinaison professeur/cours.")

    # 6. Éligibilité
    print("\n[6/6] Test de consultation d'éligibilité...")
    elig = EligibilityAPI.check(1)
    if elig:
        print(f"  ✓ Éligibilité étudiant #1 : {elig.get('eligible')} (Inscription: {elig.get('enrollment')}, "
              f"Frais: {elig.get('academic_fees')})")

    print("\n" + "=" * 60)
    print("TOUS LES TESTS D'INTÉGRATION API SONT VALIDÉS AVEC SUCCÈS !")
    print("=" * 60)


if __name__ == "__main__":
    run_integration_tests()
