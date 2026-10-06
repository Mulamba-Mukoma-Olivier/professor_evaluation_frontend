from typing import Optional, Dict, Any, List
from api.client import api_client


class EvaluationsAPI:
    """API pour la gestion des évaluations."""
    
    last_error: Optional[str] = None

    @classmethod
    def get_all(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère toutes les évaluations (admin seulement).
        
        Returns:
            Liste des évaluations
        """
        cls.last_error = None
        try:
            response = api_client.get("/evaluations")
            
            if response.status_code == 200:
                data = response.json()
                return data.get("evaluations", [])
            else:
                try:
                    cls.last_error = response.json().get("error")
                except Exception:
                    cls.last_error = f"Erreur {response.status_code}"
                return None
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la récupération des évaluations: {e}")
            return None
    
    @classmethod
    def get_by_id(cls, evaluation_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère une évaluation par son ID.
        
        Args:
            evaluation_id: ID de l'évaluation
            
        Returns:
            Dictionnaire avec les informations de l'évaluation
        """
        cls.last_error = None
        try:
            response = api_client.get(f"/evaluations/{evaluation_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    cls.last_error = response.json().get("error")
                except Exception:
                    cls.last_error = f"Erreur {response.status_code}"
                return None
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la récupération de l'évaluation: {e}")
            return None
    
    @classmethod
    def create(cls, professor_id: int, course_id: int, academic_year: str, 
               period: str, answers: List[Dict[str, int]]) -> Optional[Dict[str, Any]]:
        """
        Crée une nouvelle évaluation.
        
        Args:
            professor_id: ID du professeur
            course_id: ID du cours
            academic_year: Année académique
            period: Période
            answers: Liste de réponses [{"criterion_id": int, "score": int}]
            
        Returns:
            Dictionnaire avec l'évaluation créée, ou None en cas d'erreur
        """
        cls.last_error = None
        try:
            response = api_client.post("/evaluations", {
                "professor_id": int(professor_id),
                "course_id": int(course_id),
                "academic_year": academic_year.strip(),
                "period": period.strip(),
                "answers": answers
            })
            
            if response.status_code == 201:
                return response.json()
            else:
                try:
                    err_json = response.json()
                    cls.last_error = err_json.get("error") or f"Erreur {response.status_code}"
                except Exception:
                    cls.last_error = f"Erreur serveur ({response.status_code})"
                return None
        except Exception as e:
            cls.last_error = f"Erreur réseau: {e}"
            print(f"Erreur lors de la création de l'évaluation: {e}")
            return None

    @classmethod
    def delete(cls, evaluation_id: int) -> bool:
        """Supprime une évaluation."""
        cls.last_error = None
        try:
            response = api_client.delete(f"/evaluations/{evaluation_id}")
            if response.status_code == 200:
                return True
            try:
                cls.last_error = response.json().get("error")
            except Exception:
                cls.last_error = f"Erreur {response.status_code}"
            return False
        except Exception as e:
            cls.last_error = str(e)
            return False


from api.results_api import ResultsAPI

__all__ = ["EvaluationsAPI", "ResultsAPI"]

