from __future__ import annotations

import time
from pathlib import Path

import httpx
import jwt


def mint_app_jwt(app_id: int, private_key_pem: str) -> str:
    now = int(time.time())
    payload = {
        "iat": now - 10,
        "exp": now + 60,  # 60s lifetime
        "iss": app_id,
    }
    return jwt.encode(payload, private_key_pem, algorithm="RS256")


def load_pem_key(path: str) -> str:
    key_path = Path(path)
    if not key_path.is_file():
        msg = f"GitHub App private key not found at {path!r}"
        raise FileNotFoundError(msg)
    return key_path.read_text(encoding="utf-8")


async def get_installation_token(app_id: int, installation_id: int, pem_key_path: str) -> str:
    pem_key = load_pem_key(pem_key_path)

    jwt_token = mint_app_jwt(app_id=app_id, private_key_pem=pem_key)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
            },
        )
        res.raise_for_status()

        token = res.json().get("token")
        if not token:
            msg = "Github installation token response missing 'token'"
            raise RuntimeError(msg)
        return token
