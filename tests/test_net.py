from __future__ import annotations

import ipaddress

import pytest

import desaparecidos.net as net


def test_validate_public_http_url_rejects_local_and_private_targets() -> None:
    for url in (
        "http://localhost/service",
        "http://127.0.0.1/service",
        "http://10.1.2.3/service",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/service",
        "file:///etc/passwd",
        "https://user:secret@example.org/image.jpg",
    ):
        with pytest.raises(ValueError):
            net.validate_public_http_url(url)


def test_validate_public_http_url_accepts_public_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        net,
        "_resolved_addresses",
        lambda _hostname: {ipaddress.ip_address("93.184.216.34")},
    )
    assert net.validate_public_http_url("https://example.org/image.jpg").startswith("https://")


def test_validate_public_http_url_rejects_mixed_public_private_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        net,
        "_resolved_addresses",
        lambda _hostname: {
            ipaddress.ip_address("93.184.216.34"),
            ipaddress.ip_address("127.0.0.1"),
        },
    )
    with pytest.raises(ValueError, match="non-public"):
        net.validate_public_http_url("https://example.org/image.jpg")
