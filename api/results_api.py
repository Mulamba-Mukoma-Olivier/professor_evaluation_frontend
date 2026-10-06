from typing import Optional, Dict, Any
from api.client import api_client


class ResultsAPI:
    """API pour la consultation des résultats d'évaluation."""

    last_error: Optional[str] = None

    @classmethod
    def get_professor_result(cls, professor_id: int, course_id: int,
                              academic_year: str, period: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les résultats d'évaluation d'un professeur depuis l'API Go.
        
        Endpoint: GET /results/professors/:professor_id?course_id=...&academic_year=...&period=...

        Args:
            professor_id: ID du professeur
            course_id: ID du cours
            academic_year: Année académique (ex: '2025-2026')
            period: Période (ex: 'Semestre 1')

        Returns:
            Dictionnaire avec global_average, total_reviews, criteria, etc. ou None.
        """
        cls.last_error = None
        try:
            params = {
                "course_id": int(course_id),
                "academic_year": str(academic_year).strip(),
                "period": str(period).strip(),
            }
            response = api_client.get(f"/results/professors/{int(professor_id)}", params=params)

            if response.status_code == 200:
                return response.json()
            else:
                try:
                    err_json = response.json()
                    cls.last_error = err_json.get("error") or f"Erreur {response.status_code}"
                except Exception:
                    cls.last_error = f"Erreur serveur ({response.status_code})"
                return None
        except Exception as e:
            cls.last_error = f"Erreur réseau : {e}"
            print(f"Erreur lors de la récupération des résultats: {e}")
            return None


__all__ = ["ResultsAPI"]
