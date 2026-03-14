import os
from fastapi import Header, HTTPException, Request

RAPIDAPI_PROXY_SECRET = os.getenv("RAPIDAPI_PROXY_SECRET", "")
APILAYER_SECRET       = os.getenv("APILAYER_SECRET", "")
ZYLA_ENABLED          = os.getenv("ZYLA_ENABLED", "true").lower() == "true"


async def verify_marketplace(
    request: Request,
    x_rapidapi_proxy_secret: str = Header(None),
    x_apilayer_secret: str = Header(None),
):
    no_secrets = not any([RAPIDAPI_PROXY_SECRET, APILAYER_SECRET]) and not ZYLA_ENABLED
    if no_secrets:
        return True

    if RAPIDAPI_PROXY_SECRET and x_rapidapi_proxy_secret == RAPIDAPI_PROXY_SECRET:
        return True

    if APILAYER_SECRET and x_apilayer_secret == APILAYER_SECRET:
        return True

    if ZYLA_ENABLED and "GuzzleHttp" in (request.headers.get("user-agent", "")):
        return True

    raise HTTPException(status_code=403, detail="Access only via authorized marketplace")
