from typing import Optional, Dict, Any
from api.client import api_client


class AuthAPI:
    """API pour l'authentification (login, register)."""
    
    last_error: Optional[str] = None

    @classmethod
    def login(cls, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authentifie un utilisateur.
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            
        Returns:
            Dictionnaire avec access_token, token_type et user, ou None en cas d'erreur
        """
        cls.last_error = None
        try:
            response = api_client.post("/auth/login", {
                "email": email.strip().lower(),
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                api_client.set_token(data.get("access_token"))
                return data
            else:
                try:
                    err_json = response.json()
                    cls.last_error = err_json.get("error") or err_json.get("message") or f"Erreur {response.status_code}"
                except Exception:
                    cls.last_error = f"Erreur serveur ({response.status_code})"
                return None
        except Exception as e:
            cls.last_error = f"Impossible de joindre le serveur API: {e}"
            print(f"Erreur lors du login: {e}")
            return None
    
    @classmethod
    def register(cls, matricule: str, name: str, email: str, password: str, role: str) -> Optional[Dict[str, Any]]:
        """
        Enregistre un nouvel utilisateur.
        
        Args:
            matricule: Matricule de l'utilisateur
            name: Nom complet
            email: Email
            password: Mot de passe (min 8 caractères)
            role: Rôle (STUDENT, PROFESSOR, ADMIN)
            
        Returns:
            Dictionnaire avec message et user, ou None en cas d'erreur
        """
        cls.last_error = None
        try:
            response = api_client.post("/auth/register", {
                "matricule": matricule.strip(),
                "name": name.strip(),
                "email": email.strip().lower(),
                "password": password,
                "role": role.strip().upper()
            })
            
            if response.status_code == 201:
                return response.json()
            else:
                try:
                    err_json = response.json()
                    cls.last_error = err_json.get("error") or err_json.get("message") or f"Erreur {response.status_code}"
                except Exception:
                    cls.last_error = f"Erreur serveur ({response.status_code})"
                return None
        except Exception as e:
            cls.last_error = f"Impossible de joindre le serveur API: {e}"
            print(f"Erreur lors du register: {e}")
            return None

