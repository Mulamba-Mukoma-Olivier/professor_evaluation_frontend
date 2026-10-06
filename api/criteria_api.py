from typing import Optional, Dict, Any, List
from api.client import api_client


class CriteriaAPI:
    """API pour la gestion des critères d'évaluation."""
    
    last_error: Optional[str] = None

    @classmethod
    def get_all(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère tous les critères.
        """
        cls.last_error = None
        try:
            response = api_client.get("/criteria")
            
            if response.status_code == 200:
                data = response.json()
                return data.get("criteria", [])
            else:
                try:
                    cls.last_error = response.json().get("error")
                except Exception:
                    cls.last_error = f"Erreur {response.status_code}"
                return None
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la récupération des critères: {e}")
            return None
    
    @classmethod
    def get_active(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère les critères actifs.
        """
        cls.last_error = None
        try:
            response = api_client.get("/criteria/active")
            
            if response.status_code == 200:
                data = response.json()
                return data.get("criteria", [])
            else:
                try:
                    cls.last_error = response.json().get("error")
                except Exception:
                    cls.last_error = f"Erreur {response.status_code}"
                return None
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la récupération des critères actifs: {e}")
            return None
    
    @classmethod
    def get_by_id(cls, criteria_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un critère par son ID.
        """
        cls.last_error = None
        try:
            response = api_client.get(f"/criteria/{criteria_id}")
            
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
            print(f"Erreur lors de la récupération du critère: {e}")
            return None
    
    @classmethod
    def create(cls, name: str, description: str = "", max_score: int = 5) -> Optional[Dict[str, Any]]:
        """
        Crée un nouveau critère.
        """
        cls.last_error = None
        try:
            response = api_client.post("/criteria", {
                "name": name.strip(),
                "description": description.strip(),
                "max_score": int(max_score)
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
            print(f"Erreur lors de la création du critère: {e}")
            return None
    
    @classmethod
    def update(cls, criteria_id: int, name: str, description: str = "", max_score: int = 5,
               active: bool = True) -> Optional[Dict[str, Any]]:
        """
        Met à jour un critère.
        """
        cls.last_error = None
        try:
            response = api_client.put(f"/criteria/{criteria_id}", {
                "name": name.strip(),
                "description": description.strip(),
                "max_score": int(max_score),
                "active": bool(active)
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
            print(f"Erreur lors de la mise à jour du critère: {e}")
            return None
    
    @classmethod
    def delete(cls, criteria_id: int) -> bool:
        """
        Supprime un critère.
        """
        cls.last_error = None
        try:
            response = api_client.delete(f"/criteria/{criteria_id}")
            if response.status_code == 200:
                return True
            try:
                cls.last_error = response.json().get("error")
            except Exception:
                cls.last_error = f"Erreur {response.status_code}"
            return False
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la suppression du critère: {e}")
            return False

