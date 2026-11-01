import ipaddress, os, socket
from urllib.parse import urlparse
import requests

def _validate_url(url):
    parsed=urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname: raise ValueError("Only absolute HTTPS URLs are allowed")
    host=parsed.hostname.lower()
    allowed={x.strip().lower() for x in os.getenv("API_ALLOWED_HOSTS","").split(",") if x.strip()}
    if host not in allowed: raise PermissionError("API host is not in API_ALLOWED_HOSTS allowlist")
    try:
        for item in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM):
            ip=ipaddress.ip_address(item[4][0])
            if not ip.is_global: raise PermissionError("Private, loopback or reserved network targets are blocked")
    except socket.gaierror as exc: raise ValueError(f"Could not resolve API host: {exc}") from exc
    return url

def call_api(url,method="GET",params=None,data=None):
    try:
        url=_validate_url(url); method=method.upper()
        if method not in {"GET","POST"}: raise ValueError("Only GET and POST are supported")
        response=requests.request(method,url,params=params,json=data,timeout=(3,10),allow_redirects=False)
        if 300 <= response.status_code < 400: raise ValueError("Redirects are blocked for SSRF protection")
        response.raise_for_status()
        try: payload=response.json()
        except ValueError: payload=response.text[:20000]
        return {"status":"success","status_code":response.status_code,"data":payload}
    except Exception as exc: return {"status":"failed","error":str(exc)}
