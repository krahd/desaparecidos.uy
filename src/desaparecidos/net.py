from __future__ import annotations

import ipaddress
import socket
from typing import Any, Protocol
from urllib.parse import urljoin, urlsplit

import requests

MAX_REDIRECTS = 5


class RequestClient(Protocol):
    def get(self, url: str, **kwargs: Any) -> requests.Response: ...


def _resolved_addresses(hostname: str) -> set[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    addresses: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
    try:
        records = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"cannot resolve host {hostname!r}") from exc
    for record in records:
        addresses.add(ipaddress.ip_address(record[4][0]))
    if not addresses:
        raise ValueError(f"host {hostname!r} resolved to no addresses")
    return addresses


def _is_public(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    )


def validate_public_http_url(url: str) -> str:
    """Reject local, credential-bearing, and non-HTTP network targets.

    This is a local application, but crawler and download URLs are supplied by a
    user-facing API. Treating them as public-network-only prevents those routes
    from becoming a path to loopback services, private networks, cloud metadata,
    or credential-bearing URLs.
    """
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"unsupported URL scheme: {parsed.scheme or '(missing)'}")
    if not parsed.hostname:
        raise ValueError("URL host is required")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("credential-bearing URLs are not allowed")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("localhost URLs are not allowed")
    try:
        literal = ipaddress.ip_address(hostname)
        addresses = {literal}
    except ValueError:
        addresses = _resolved_addresses(hostname)
    blocked = sorted(str(address) for address in addresses if not _is_public(address))
    if blocked:
        raise ValueError(f"URL resolves to a non-public address: {', '.join(blocked)}")
    return url


def safe_get(
    client: RequestClient,
    url: str,
    *,
    timeout: int | float,
    headers: dict[str, str] | None = None,
    max_redirects: int = MAX_REDIRECTS,
    **kwargs: Any,
) -> requests.Response:
    """GET a public HTTP(S) resource while validating every redirect target."""
    current = url
    for _ in range(max_redirects + 1):
        validate_public_http_url(current)
        response = client.get(
            current,
            timeout=timeout,
            headers=headers,
            allow_redirects=False,
            **kwargs,
        )
        if response.status_code not in {301, 302, 303, 307, 308}:
            return response
        location = response.headers.get("location")
        if not location:
            return response
        current = urljoin(current, location)
    raise ValueError(f"too many redirects while fetching {url}")
