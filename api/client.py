import requests
from typing import Optional, Dict, Any
from config import API_BASE_URL


class APIClient:
    """Client HTTP de base pour communiquer avec l'API REST Go."""

    def __init__(self, base_url: str = API_BASE_URL, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.timeout = timeout

    def set_token(self, token: Optional[str]):
        """Stocke le token JWT pour l'authentification."""
        self.token = token

    def clear_token(self):
        """Supprime le token JWT."""
        self.token = None
        # Import différé pour éviter un cycle entre le client et le stockage.
        try:
            from logic.session_store import SessionStore
            SessionStore.clear()
        except ImportError:
            pass

    def is_authenticated(self) -> bool:
        """Indique si un token est présent."""
        return bool(self.token)

    def _get_headers(self) -> Dict[str, str]:
        """Retourne les headers avec le token si disponible."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Effectue une requête GET."""
        url = f"{self.base_url}{endpoint}"
        return self._handle_response(requests.get(url, headers=self._get_headers(), params=params, timeout=self.timeout))

    def post(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        """Effectue une requête POST."""
        url = f"{self.base_url}{endpoint}"
        return self._handle_response(requests.post(url, headers=self._get_headers(), json=data, timeout=self.timeout))

    def put(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        """Effectue une requête PUT."""
        url = f"{self.base_url}{endpoint}"
        return self._handle_response(requests.put(url, headers=self._get_headers(), json=data, timeout=self.timeout))

    def delete(self, endpoint: str) -> requests.Response:
        """Effectue une requête DELETE."""
        url = f"{self.base_url}{endpoint}"
        return self._handle_response(requests.delete(url, headers=self._get_headers(), timeout=self.timeout))

    def _handle_response(self, response: requests.Response) -> requests.Response:
        # Une session révoquée côté serveur ne doit pas être restaurée au prochain démarrage.
        if response.status_code == 401 and self.token:
            self.clear_token()
        return response


# Instance globale du client API
api_client = APIClient()

