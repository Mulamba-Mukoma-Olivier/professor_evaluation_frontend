from typing import Optional, Dict, Any
from api.client import api_client


class EligibilityAPI:
    """API pour la gestion de l'éligibilité des étudiants."""
    
    last_error: Optional[str] = None

    @classmethod
    def check(cls, student_id: int) -> Optional[Dict[str, Any]]:
        """
        Vérifie l'éligibilité d'un étudiant.
        
        Args:
            student_id: ID de l'étudiant
            
        Returns:
            Dictionnaire avec les informations d'éligibilité
        """
        cls.last_error = None
        try:
            response = api_client.get(f"/eligibility/{student_id}")
            
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
            print(f"Erreur lors de la vérification de l'éligibilité: {e}")
            return None
    
    @classmethod
    def create(cls, student_id: int, enrollment: bool, academic_fees: bool,
               laboratory_fees: bool, access_fees: bool) -> Optional[Dict[str, Any]]:
        """
        Crée une éligibilité pour un étudiant.
        """
        cls.last_error = None
        try:
            response = api_client.post("/eligibility", {
                "student_id": int(student_id),
                "enrollment": bool(enrollment),
                "academic_fees": bool(academic_fees),
                "laboratory_fees": bool(laboratory_fees),
                "access_fees": bool(access_fees)
            })
            
            if response.status_code == 201:
                return response.json()
            else:
                try:
                    cls.last_error = response.json().get("error")
                except Exception:
                    cls.last_error = f"Erreur {response.status_code}"
                return None
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la création de l'éligibilité: {e}")
            return None
    
    @classmethod
    def update(cls, student_id: int, enrollment: bool, academic_fees: bool,
               laboratory_fees: bool, access_fees: bool) -> Optional[Dict[str, Any]]:
        """
        Met à jour l'éligibilité d'un étudiant.
        """
        cls.last_error = None
        try:
            response = api_client.put(f"/eligibility/{student_id}", {
                "enrollment": bool(enrollment),
                "academic_fees": bool(academic_fees),
                "laboratory_fees": bool(laboratory_fees),
                "access_fees": bool(access_fees)
            })
            
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
            print(f"Erreur lors de la mise à jour de l'éligibilité: {e}")
            return None
    
    @classmethod
    def delete(cls, student_id: int) -> bool:
        """
        Supprime l'éligibilité d'un étudiant.
        """
        cls.last_error = None
        try:
            response = api_client.delete(f"/eligibility/{student_id}")
            if response.status_code == 200:
                return True
            try:
                cls.last_error = response.json().get("error")
            except Exception:
                cls.last_error = f"Erreur {response.status_code}"
            return False
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la suppression de l'éligibilité: {e}")
            return False

