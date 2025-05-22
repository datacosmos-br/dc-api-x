"""
Authentication provider interfaces for DCApiX.

This module contains base interfaces for authentication providers
that can be implemented by external packages.
"""

from .basic import BasicAuthProvider
from .database import DatabaseAuthProvider
from .ldap import LdapAuthProvider
from .oauth import OAuthProvider
from .provider import AuthProvider
from .token import TokenAuthProvider

__all__ = [
    "AuthProvider",
    "BasicAuthProvider",
    "TokenAuthProvider",
    "OAuthProvider",
    "LdapAuthProvider",
    "DatabaseAuthProvider",
]
