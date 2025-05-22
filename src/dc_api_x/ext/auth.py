"""
Authentication provider interfaces for DCApiX.

This module defines interfaces for authentication providers that can be
implemented by external packages to handle authentication for different protocols.

This is a facade that re-exports all auth providers from the auth subdirectory.
"""

from .auth.basic import BasicAuthProvider
from .auth.database import DatabaseAuthProvider
from .auth.ldap import LdapAuthProvider
from .auth.oauth import OAuthProvider
from .auth.provider import AuthProvider
from .auth.token import TokenAuthProvider

__all__ = [
    "AuthProvider",
    "BasicAuthProvider",
    "TokenAuthProvider",
    "OAuthProvider",
    "LdapAuthProvider",
    "DatabaseAuthProvider",
]
