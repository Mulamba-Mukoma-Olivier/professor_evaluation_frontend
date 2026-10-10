"""Persistance locale de la session utilisateur (sans mot de passe)."""

import base64
import json
import time
from typing import Any, Dict, Optional

from PyQt5.QtCore import QSettings


class SessionStore:
    TOKEN_KEY = "session/access_token"
    USER_KEY = "session/user"

    @classmethod
    def _settings(cls):
        # L'identité doit correspondre à l'application afin que les sessions
        # restent disponibles au prochain lancement.
        return QSettings("Professor Evaluation", "Professor Evaluation")

    @staticmethod
    def _is_expired(token: str) -> bool:
        """Lit exp pour éviter de restaurer un JWT manifestement expiré.

        La signature reste validée par l'API lors des requêtes authentifiées.
        """
        try:
            payload = token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            claims = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
            expiry = claims.get("exp")
            return expiry is not None and float(expiry) <= time.time()
        except (IndexError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
            # Les tokens non-JWT/illisibles ne sont pas rejetés ici; le serveur
            # reste l'autorité pour leur validation.
            return False

    @classmethod
    def save(cls, token: str, user: Dict[str, Any]) -> None:
        if not token or not isinstance(user, dict):
            cls.clear()
            return
        settings = cls._settings()
        settings.setValue(cls.TOKEN_KEY, token)
        settings.setValue(cls.USER_KEY, json.dumps(user, ensure_ascii=False))
        settings.sync()

    @classmethod
    def restore(cls) -> Optional[Dict[str, Any]]:
        settings = cls._settings()
        token = settings.value(cls.TOKEN_KEY, "", type=str)
        user_json = settings.value(cls.USER_KEY, "", type=str)
        if not token or cls._is_expired(token):
            cls.clear()
            return None
        try:
            user = json.loads(user_json)
            if not isinstance(user, dict):
                raise ValueError("Profil de session invalide")
        except (json.JSONDecodeError, TypeError, ValueError):
            cls.clear()
            return None

        from api.client import api_client
        api_client.set_token(token)
        return user

    @classmethod
    def clear(cls) -> None:
        settings = cls._settings()
        settings.remove(cls.TOKEN_KEY)
        settings.remove(cls.USER_KEY)
        settings.sync()
        from api.client import api_client
        api_client.set_token(None)
