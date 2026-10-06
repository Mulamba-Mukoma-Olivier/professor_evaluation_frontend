from typing import Optional, Dict, Any, List
from api.client import api_client


class CoursesAPI:
    """API pour la gestion des cours."""
    
    last_error: Optional[str] = None

    @classmethod
    def get_all(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère tous les cours.
        """
        cls.last_error = None
        try:
            response = api_client.get("/courses")
            
            if response.status_code == 200:
                data = response.json()
                return data.get("courses", [])
            else:
                try:
                    cls.last_error = response.json().get("error")
                except Exception:
                    cls.last_error = f"Erreur {response.status_code}"
                return None
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la récupération des cours: {e}")
            return None
    
    @classmethod
    def get_by_id(cls, course_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un cours par son ID.
        """
        cls.last_error = None
        try:
            response = api_client.get(f"/courses/{course_id}")
            
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
            print(f"Erreur lors de la récupération du cours: {e}")
            return None
    
    @classmethod
    def create(cls, code: str, name: str, description: str = "", 
                department: str = "", academic_year: str = "") -> Optional[Dict[str, Any]]:
        """
        Crée un nouveau cours.
        """
        cls.last_error = None
        try:
            response = api_client.post("/courses", {
                "code": code.strip(),
                "name": name.strip(),
                "description": description.strip(),
                "department": department.strip(),
                "academic_year": academic_year.strip()
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
            print(f"Erreur lors de la création du cours: {e}")
            return None
    
    @classmethod
    def update(cls, course_id: int, code: str, name: str, description: str = "",
                department: str = "", academic_year: str = "") -> Optional[Dict[str, Any]]:
        """
        Met à jour un cours.
        """
        cls.last_error = None
        try:
            response = api_client.put(f"/courses/{course_id}", {
                "code": code.strip(),
                "name": name.strip(),
                "description": description.strip(),
                "department": department.strip(),
                "academic_year": academic_year.strip()
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
            print(f"Erreur lors de la mise à jour du cours: {e}")
            return None
    
    @classmethod
    def delete(cls, course_id: int) -> bool:
        """
        Supprime un cours.
        """
        cls.last_error = None
        try:
            response = api_client.delete(f"/courses/{course_id}")
            if response.status_code == 200:
                return True
            try:
                cls.last_error = response.json().get("error")
            except Exception:
                cls.last_error = f"Erreur {response.status_code}"
            return False
        except Exception as e:
            cls.last_error = str(e)
            print(f"Erreur lors de la suppression du cours: {e}")
            return False

