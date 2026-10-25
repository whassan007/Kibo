"""Verified enterprise identities. SAML assertions must be exchanged by a trusted IdP.

Configure KIBO_JWT_ISSUER, KIBO_JWT_AUDIENCE and a signing secret or RSA
public key. OIDC/Entra deployments may supply a trusted JWKS client explicitly.
No issuer or key discovery is performed from untrusted token claims.
"""
import os
import time
from dataclasses import dataclass, field
from typing import Any, Mapping

from fastapi import HTTPException


@dataclass(frozen=True)
class PrincipalContext:
    user_id: str
    tenant_id: str
    roles: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    residency_region: str | None = None
    issuer: str = ""
    expires_at: float | None = None
    authenticated: bool = True
    claims: Mapping[str, Any] = field(default_factory=dict, repr=False)

    @property
    def sub(self):
        return self.user_id

    @property
    def tid(self):
        return self.tenant_id


def strict_auth_enabled() -> bool:
    return os.getenv("KIBO_STRICT_AUTH", "").lower() in {"1", "true", "yes"}


def _strings(value):
    if isinstance(value, str):
        return tuple(value.split())
    if isinstance(value, (list, tuple)) and all(isinstance(v, str) for v in value):
        return tuple(value)
    raise ValueError("Invalid role or scope claims")


def verify_enterprise_token(token: str, *, key=None, issuer=None, audience=None,
                            algorithms=None, jwks_client=None, saml_verifier=None,
                            token_type="jwt") -> PrincipalContext:
    """Verify signed JWTs or assertions using a deployment-owned SAML verifier.

    A SAML verifier must validate signature, audience, recipient, time bounds,
    InResponseTo and replay protection and return normalized JWT-style claims.
    """
    try:
        expected_issuer = issuer or os.getenv("KIBO_JWT_ISSUER")
        expected_audience = audience or os.getenv("KIBO_JWT_AUDIENCE")
        if token_type.lower() == "saml":
            if saml_verifier is None or not expected_issuer or not expected_audience:
                raise ValueError("Trusted SAML verifier and issuer/audience required")
            claims = saml_verifier(token, issuer=expected_issuer, audience=expected_audience)
        else:
            import jwt
            configured_alg = os.getenv("KIBO_JWT_ALGORITHM", "HS256")
            allowed = list(algorithms or [configured_alg])
            if not allowed or any(a not in {"HS256", "HS384", "HS512", "RS256", "RS384", "RS512"} for a in allowed):
                raise ValueError("Unsupported signing algorithm")
            if any(a.startswith("HS") for a in allowed) and any(a.startswith("RS") for a in allowed):
                raise ValueError("Cannot mix symmetric and asymmetric algorithms")
            signing_key = key or (os.getenv("KIBO_JWT_PUBLIC_KEY") if allowed[0].startswith("RS") else os.getenv("KIBO_JWT_SECRET"))
            if jwks_client is not None:
                if any(not a.startswith("RS") for a in allowed):
                    raise ValueError("JWKS requires RSA")
                signing_key = jwks_client.get_signing_key_from_jwt(token).key
            if not signing_key or not expected_issuer:
                raise ValueError("Token verification is not configured")
            claims = jwt.decode(token, signing_key, algorithms=allowed,
                                issuer=expected_issuer, audience=expected_audience,
                                options={"require": ["sub", "tid", "iss", "exp"],
                                         "verify_aud": bool(expected_audience)})
        if claims.get("iss") != expected_issuer or float(claims["exp"]) <= time.time():
            raise ValueError("Expired token or incorrect issuer")
        for name in ("sub", "tid"):
            if not isinstance(claims.get(name), str) or not claims[name].strip():
                raise ValueError("Missing identity claim")
        return PrincipalContext(
            user_id=claims["sub"], tenant_id=claims["tid"],
            roles=_strings(claims.get("roles", [])),
            scopes=_strings(claims.get("scopes", claims.get("scp", []))),
            residency_region=claims.get("residency_region"), issuer=claims["iss"],
            expires_at=float(claims["exp"]), claims=dict(claims))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid enterprise token",
                            headers={"WWW-Authenticate": "Bearer"}) from exc


def create_tenant_jwt(user_id: str, tenant_id: str, roles=(), scopes=(),
                      residency_region=None, *, key=None, issuer=None, audience=None,
                      expires_in=3600, algorithm=None) -> str:
    import jwt
    algorithm = algorithm or os.getenv("KIBO_JWT_ALGORITHM", "HS256")
    if algorithm not in {"HS256", "HS384", "HS512", "RS256", "RS384", "RS512"}:
        raise ValueError("Unsupported signing algorithm")
    key = key or os.getenv("KIBO_JWT_PRIVATE_KEY" if algorithm.startswith("RS") else "KIBO_JWT_SECRET")
    issuer = issuer or os.getenv("KIBO_JWT_ISSUER")
    if not key or not issuer or not user_id or not tenant_id or expires_in <= 0:
        raise ValueError("Signing configuration and identity are required")
    now = int(time.time())
    claims = dict(sub=user_id, tid=tenant_id, roles=list(_strings(roles)),
                  scopes=list(_strings(scopes)), residency_region=residency_region,
                  iss=issuer, iat=now, exp=now + expires_in)
    audience = audience or os.getenv("KIBO_JWT_AUDIENCE")
    if audience:
        claims["aud"] = audience
    return jwt.encode(claims, key, algorithm=algorithm)


def principal_from_request(request) -> PrincipalContext:
    authorization = request.headers.get("Authorization", "")
    tenant = request.headers.get("X-Tenant-ID")
    user = request.headers.get("X-User-ID")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer" and token and ("." in token or strict_auth_enabled()):
        principal = verify_enterprise_token(token)
        request.state.principal = principal
        if tenant and tenant != principal.tenant_id:
            raise HTTPException(403, "Cross-tenant access attempt blocked")
        if user and user != principal.user_id:
            raise HTTPException(403, "User identity mismatch")
        return principal
    if strict_auth_enabled():
        raise HTTPException(401, "Verified enterprise token required")
    # Explicitly unverified compatibility identity; membership is still required.
    return PrincipalContext(user_id=user or token or "user_expert",
                            tenant_id=tenant or "default", authenticated=False)
