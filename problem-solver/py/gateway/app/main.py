import os
import time
import logging
import hashlib
from functools import lru_cache

import httpx
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("ostis-ann-gateway")

LOG_RAW_TOKENS = os.getenv("LOG_RAW_TOKENS", "false").lower() == "true"

def mask_token(tok: str) -> str:
    if not tok:
        return ""
    if len(tok) <= 10:
        return "*" * len(tok)
    return tok[:6] + "..." + tok[-4:]

def token_fingerprint(tok: str) -> str:
    h = hashlib.sha256(tok.encode("utf-8")).hexdigest()
    return h[:16]

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
REALM = os.getenv("KEYCLOAK_REALM", "ostis-ann")
RESOURCE_AUDIENCE = os.getenv("RESOURCE_AUDIENCE", "backend-service")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",")]
TARGET_API = os.getenv("TARGET_API", "http://api:8000")
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
ISSUER = f"{KEYCLOAK_URL}/realms/{REALM}"
TOKEN_ISSUER = os.getenv("TOKEN_ISSUER", ISSUER)

_JWKS = None
_JWKS_TS = 0
_JWKS_TTL = int(os.getenv("JWKS_TTL", "300"))

app = FastAPI(title="OSTIS ANN Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

def fetch_jwks():
    global _JWKS, _JWKS_TS
    now = time.time()
    if _JWKS and (now - _JWKS_TS) < _JWKS_TTL:
        return _JWKS
    r = httpx.get(JWKS_URL, timeout=5.0)
    r.raise_for_status()
    _JWKS = r.json()
    _JWKS_TS = now
    return _JWKS

def get_jwk_for_kid(kid: str):
    jwks = fetch_jwks()
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            return k

    global _JWKS_TS
    _JWKS_TS = 0
    jwks = fetch_jwks()
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            return k
    return None

def get_bearer_token(request: Request) -> str:
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = auth.split(" ", 1)[1].strip()

    try:
        masked = mask_token(token)
        fp = token_fingerprint(token)
        logger.info("Received bearer token: masked=%s fingerprint=%s client=%s path=%s",
                    masked, fp,
                    request.client.host if request.client else "unknown",
                    request.url.path)
        if LOG_RAW_TOKENS:
            logger.warning("RAW TOKEN (insecure logging enabled): %s", token)
    except Exception as e:
        logger.exception("Failed to log token info: %s", e)

    return token

def verify_jwt(token: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)
        logger.debug(f"JWT header: {header}")
    except JWTError as e:
        logger.error(f"Failed to decode JWT header: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid JWT header")

    kid = header.get("kid")
    if not kid:
        logger.error("Missing kid in token header")
        raise HTTPException(status_code=401, detail="Missing kid in token header")

    logger.debug(f"Looking for JWK with kid: {kid}")
    jwk = get_jwk_for_kid(kid)
    if not jwk:
        logger.error(f"JWK not found for kid: {kid}")
        raise HTTPException(status_code=401, detail="Public key not found (kid)")

    token_issuer = None
    try:
        claims_unverified = jwt.decode(
            token, 
            jwk, 
            algorithms=["RS256"], 
            options={
                "verify_signature": True, 
                "verify_iss": False, 
                "verify_exp": False,
                "verify_aud": False
            }
        )
        token_issuer = claims_unverified.get("iss")
        token_aud = claims_unverified.get("aud")
        token_exp = claims_unverified.get("exp")
        logger.info(f"Token details - issuer: {token_issuer}, expected: {TOKEN_ISSUER}, audience: {token_aud}, exp: {token_exp}")
        
        if token_issuer != TOKEN_ISSUER:
            logger.error(f"Issuer mismatch: token has '{token_issuer}', expected '{TOKEN_ISSUER}'")
            raise HTTPException(
                status_code=401, 
                detail=f"Invalid token issuer. Got: {token_issuer}, expected: {TOKEN_ISSUER}. Update TOKEN_ISSUER env var."
            )

        claims = jwt.decode(
            token,
            jwk,
            algorithms=["RS256"],
            issuer=TOKEN_ISSUER,
            options={
                "verify_signature": True, 
                "verify_iss": True, 
                "verify_exp": True,
                "verify_aud": False
            },
        )
        logger.info(f"Token verified successfully. Subject: {claims.get('sub')}, Issuer: {claims.get('iss')}")
    except HTTPException:
        raise
    except JWTError as e:
        error_msg = str(e)
        logger.error(f"Token verification failed: {error_msg}")
        logger.error(f"  Token issuer: {token_issuer or 'unknown'}")
        logger.error(f"  Expected issuer: {TOKEN_ISSUER}")
        if token_issuer and token_issuer != TOKEN_ISSUER:
            logger.error(f"  ISSUER MISMATCH! Update TOKEN_ISSUER env var to: {token_issuer}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {error_msg}")

    return claims

async def proxy_request(target_base: str, request: Request, path_suffix: str):
    url = f"{target_base}{path_suffix}"
    method = request.method
    headers = {k: v for k, v in request.headers.items() if k.lower() not in (
        "host", "content-length", "transfer-encoding", "connection", "authorization"
    )}

    headers["X-Forwarded-For"] = request.client.host if request.client else ""
    headers["X-Forwarded-Proto"] = "https" if os.getenv("FORCE_HTTPS", "false").lower() == "true" else "http"

    body = await request.body()
    logger.info(f"Proxy request: {method} {url} (body size: {len(body)} bytes)")
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            resp = await client.request(method, url, headers=headers, content=body, params=request.query_params)
            logger.info(f"Proxy response: {resp.status_code} from {url}")
            
            response_content = await resp.aread()
            
            response_headers = {
                k: v for k, v in resp.headers.items() 
                if k.lower() not in ("content-encoding", "transfer-encoding", "content-length")
            }
            
            # Preserve CORS headers from backend
            cors_headers = ["access-control-allow-origin", "access-control-allow-credentials", 
                          "access-control-allow-methods", "access-control-allow-headers",
                          "access-control-expose-headers"]
            for header in cors_headers:
                if header in resp.headers:
                    response_headers[header] = resp.headers[header]
            
            response_headers["Content-Length"] = str(len(response_content))
            
            from fastapi.responses import Response
            return Response(
                content=response_content,
                status_code=resp.status_code,
                headers=response_headers,
                media_type=resp.headers.get("content-type")
            )
        except Exception as e:
            logger.error(f"Proxy error for {url}: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Backend error: {str(e)}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return JSONResponse({"service": "gateway", "status": "ok"})

@app.get("/whoami")
def whoami(token: str = Depends(get_bearer_token)):
    claims = verify_jwt(token)
    return {"sub": claims.get("sub"), "preferred_username": claims.get("preferred_username"), "email": claims.get("email")}

KC_PREFIX = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect"

@app.api_route("/auth/{full_path:path}", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def keycloak_proxy(full_path: str, request: Request):
    return await proxy_request(KC_PREFIX, request, f"/{full_path}")

@app.api_route("/api/{full_path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
async def api_proxy(full_path: str, request: Request):
    # Handle preflight OPTIONS requests without authentication
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
                "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
        )
    
    try:
        token = get_bearer_token(request)
        claims = verify_jwt(token)
        request.state.user = {"sub": claims.get("sub"), "claims": claims}
        target_url = f"{TARGET_API}/api/{full_path}"
        logger.info(f"Proxying {request.method} {request.url.path} -> {target_url}")
        return await proxy_request(TARGET_API, request, f"/api/{full_path}")
    except HTTPException as e:
        logger.error(f"HTTP error in api_proxy: {e.status_code} - {e.detail} - path: {request.url.path}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in api_proxy: {str(e)} - path: {request.url.path}", exc_info=True)
        raise

@app.api_route("/{full_path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
async def direct_api_proxy(full_path: str, request: Request):

    if full_path in ("health", "whoami", "") or full_path.startswith("auth/") or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    token = get_bearer_token(request)
    claims = verify_jwt(token)
    request.state.user = {"sub": claims.get("sub"), "claims": claims}
    
    target_url = f"{TARGET_API}/{full_path}"
    logger.info(f"Direct proxying {request.method} /{full_path} -> {target_url}")
    return await proxy_request(TARGET_API, request, f"/{full_path}")
