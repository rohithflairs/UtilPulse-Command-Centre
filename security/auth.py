"""
UtilPulse Command Centre — Authenticator
==========================================
Simple credential validation against the USERS dict defined in config.
"""

from config import USERS


class Authenticator:
    """Handles user authentication for UtilPulse Command Centre."""

    @staticmethod
    def authenticate(username: str, password: str) -> dict | None:
        """Validate username/password against the USERS configuration.

        Parameters
        ----------
        username : str
            Login username.
        password : str
            Plain-text password to verify.

        Returns
        -------
        dict | None
            ``{username, name, role, designation}`` on success, ``None`` on
            failure.
        """
        user = USERS.get(username)
        if user and user["password"] == password:
            return {
                "username": username,
                "name": user["name"],
                "role": user["role"],
                "designation": user["designation"],
            }
        return None

    @staticmethod
    def get_user_display(user_info: dict | None) -> str:
        """Return a formatted display string: ``'Name | Designation'``.

        Parameters
        ----------
        user_info : dict | None
            User info dict as returned by :meth:`authenticate`.

        Returns
        -------
        str
            Human-readable label, or empty string if *user_info* is falsy.
        """
        if user_info:
            return f"{user_info['name']} | {user_info['designation']}"
        return ""
