"""
Deprecated compatibility shim.

`replit_auth.py` has been replaced by `auth.py` (generic auth names).
This module re-exports the public symbols from `auth.py` to preserve
backwards compatibility for any imports that still reference
`flask_dashboard.replit_auth`.
"""

from .auth import *  # noqa: F401,F403
