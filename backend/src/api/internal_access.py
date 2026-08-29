"""Access control for same-machine internal API routes."""

from __future__ import annotations

from ipaddress import ip_address, ip_network

from fastapi import HTTPException, Request

_PRIVATE_NETWORKS = (
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
)
_FORWARDED_HEADERS = ("x-forwarded-for", "x-real-ip")
_FORBIDDEN_DETAIL = "Localhost only"


def _header_value(request: Request, name: str) -> str:
    headers = getattr(request, "headers", None)
    if headers is None:
        return ""
    getter = getattr(headers, "get", None)
    if getter is None:
        return ""
    value = getter(name)
    if value is None:
        return ""
    return str(value).strip()


def _has_forwarded_client(request: Request) -> bool:
    return any(_header_value(request, name) for name in _FORWARDED_HEADERS)


def _is_internal_peer(host: str) -> bool:
    if not host:
        return False
    try:
        addr = ip_address(host)
    except ValueError:
        return False
    if addr.version == 6 and getattr(addr, "ipv4_mapped", None) is not None:
        addr = addr.ipv4_mapped
    if addr.is_loopback:
        return True
    return any(addr in network for network in _PRIVATE_NETWORKS)


def require_localhost(request: Request) -> None:
    if _has_forwarded_client(request):
        raise HTTPException(status_code=403, detail=_FORBIDDEN_DETAIL)
    host = request.client.host if request.client else ""
    if not _is_internal_peer(host):
        raise HTTPException(status_code=403, detail=_FORBIDDEN_DETAIL)
