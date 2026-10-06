from typing import Optional, Dict, Any, List
from api.client import api_client


class ProfessorsAPI:
    """API pour la gestion des professeurs."""
    
    last_error: Optional[str] = None

    @classmethod
    def get_all(cls, page: int = 1, page_size: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère tous les professeurs avec pagination.
        """
        cls.last_error = None
        try:
            response = api_client.get("/professors", {
                "page": page,
                "page_size": page_size
            })
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                try:
                    cls.last_error = response.json().get("error")
                except Exception:
                    cls.last_error = f"Erreur {response.status_code}"
                return None
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la récupération des professeurs: {e}")
            return None
    
    @classmethod
    def get_active(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère les professeurs actifs.
        """
        cls.last_error = None
        try:
            response = api_client.get("/professors/active")
            
            if response.status_code == 200:
                data = response.json()
                return data.get("professors", [])
            else:
                try:
                    cls.last_error = response.json().get("error")
                except Exception:
                    cls.last_error = f"Erreur {response.status_code}"
                return None
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la récupération des professeurs actifs: {e}")
            return None
    
    @classmethod
    def get_by_status(cls, status: str) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère les professeurs par statut.
        """
        cls.last_error = None
        try:
            response = api_client.get("/professors/by-status", {
                "status": status
            })
            
            if response.status_code == 200:
                data = response.json()
                return data.get("professors", [])
            else:
                try:
                    cls.last_error = response.json().get("error")
                except Exception:
                    cls.last_error = f"Erreur {response.status_code}"
                return None
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la récupération des professeurs par statut: {e}")
            return None
    
    @classmethod
    def get_by_id(cls, professor_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un professeur par son ID.
        """
        cls.last_error = None
        try:
            response = api_client.get(f"/professors/{professor_id}")
            
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
            print(f"Erreur lors de la récupération du professeur: {e}")
            return None
    
    @classmethod
    def create(cls, matricule: str, first_name: str, last_name: str, 
               email: str, department: str, grade: str = "", 
               status: str = "active") -> Optional[Dict[str, Any]]:
        """
        Crée un nouveau professeur.
        """
        cls.last_error = None
        try:
            payload = {
                "matricule": matricule.strip(),
                "first_name": first_name.strip(),
                "last_name": last_name.strip(),
                "department": department.strip(),
                "status": status or "active"
            }
            if email and email.strip():
                payload["email"] = email.strip().lower()
            if grade and grade.strip():
                payload["grade"] = grade.strip()

            response = api_client.post("/professors", payload)
            
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
            print(f"Erreur lors de la création du professeur: {e}")
            return None
    
    @classmethod
    def update(cls, professor_id: int, matricule: str, first_name: str, last_name: str,
               email: str, department: str, grade: str = "", active: bool = True,
               status: str = "active") -> Optional[Dict[str, Any]]:
        """
        Met à jour un professeur.
        """
        cls.last_error = None
        try:
            payload = {
                "matricule": matricule.strip(),
                "first_name": first_name.strip(),
                "last_name": last_name.strip(),
                "department": department.strip(),
                "active": bool(active),
                "status": status or "active"
            }
            if email and email.strip():
                payload["email"] = email.strip().lower()
            if grade and grade.strip():
                payload["grade"] = grade.strip()

            response = api_client.put(f"/professors/{professor_id}", payload)
            
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
            print(f"Erreur lors de la mise à jour du professeur: {e}")
            return None
    
    @classmethod
    def delete(cls, professor_id: int) -> bool:
        """
        Supprime un professeur.
        """
        cls.last_error = None
        try:
            response = api_client.delete(f"/professors/{professor_id}")
            if response.status_code == 200:
                return True
            try:
                cls.last_error = response.json().get("error")
            except Exception:
                cls.last_error = f"Erreur {response.status_code}"
            return False
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la suppression du professeur: {e}")
            return False

