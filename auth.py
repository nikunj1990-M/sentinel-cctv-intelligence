"""Minimal RBAC/session stub for the demo dashboard.

NOT production-grade auth (no rate limiting, lockout, or password policy) - this exists
to demonstrate role-gated access (admin vs operator) for the hackathon HLD, using only
the stdlib (hashlib/secrets) so no new dependency is needed.
"""
import hashlib
import secrets
import time

SESSION_TTL_SECONDS = 8 * 60 * 60  # 8h shift

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Demo users only - in a real deployment this would be a Postgres table with
# properly salted/hashed passwords behind an identity provider (e.g. SSO/eGujCop AD).
USERS = {
    "admin": {"password_hash": _hash("sentinel123"), "role": "admin"},
    "operator": {"password_hash": _hash("watch123"), "role": "operator"},
}

_sessions: dict[str, dict] = {}

def verify_login(username: str, password: str):
    user = USERS.get(username)
    if user and user["password_hash"] == _hash(password):
        return user["role"]
    return None

def create_session(username: str, role: str) -> str:
    token = secrets.token_hex(32)
    _sessions[token] = {"username": username, "role": role, "created": time.time()}
    return token

def get_session(token: str | None):
    if not token:
        return None
    session = _sessions.get(token)
    if not session:
        return None
    if time.time() - session["created"] > SESSION_TTL_SECONDS:
        _sessions.pop(token, None)
        return None
    return session

def destroy_session(token: str | None):
    if token:
        _sessions.pop(token, None)
