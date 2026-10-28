import hashlib
import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from .logging import get_logger

logger = get_logger(__name__)

# Private and restricted IPv4 and IPv6 networks
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
]

BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
    "instance-data",
}


def is_ip_blocked(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if (
        ip_obj.is_loopback
        or ip_obj.is_private
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_unspecified
    ):
        return True
    for net in BLOCKED_NETWORKS:
        if ip_obj in net:
            return True
    return False


def is_safe_url(url: str) -> tuple[bool, str]:
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Malformed URL: {e}"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Disallowed scheme: '{parsed.scheme}'. Only HTTP and HTTPS are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in URL"

    lower_host = hostname.lower()
    if (
        lower_host in BLOCKED_HOSTNAMES
        or lower_host.endswith(".local")
        or lower_host.endswith(".internal")
    ):
        return False, f"Prohibited hostname: {hostname}"

    # Try parsing hostname as an IP literal
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if is_ip_blocked(ip_obj):
            return False, f"Direct access to private or loopback IP '{hostname}' is blocked."
        return True, "Safe"
    except ValueError:
        pass  # Not an IP literal, proceed to DNS resolution

    # Resolve hostname to verify destination IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            if is_ip_blocked(ip_obj):
                return (
                    False,
                    f"Hostname '{hostname}' resolves to blocked private/local address {ip_str}.",
                )
    except socket.gaierror as e:
        return False, f"Failed to resolve host '{hostname}': {e}"
    except Exception as e:
        return False, f"DNS validation error for '{hostname}': {e}"

    return True, "Safe"


def calculate_content_hash(text: str) -> str:
    """Computes a canonical SHA-256 hash of a content string."""
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


async def safe_fetch_url(
    client: httpx.AsyncClient,
    url: str,
    max_size_bytes: int = 1_000_000,
    max_redirects: int = 3,
    timeout: float = 10.0,
) -> tuple[str, str]:
    """
    Safely fetches a web resource with SSRF protection, size bounding, and redirect validation.
    Returns (content_text, content_hash).
    """
    current_url = url
    redirect_count = 0

    while True:
        is_safe, reason = is_safe_url(current_url)
        if not is_safe:
            raise ValueError(f"SSRF Protection blocked request to {current_url}: {reason}")

        response = await client.get(
            current_url,
            follow_redirects=False,
            timeout=timeout,
            headers={"User-Agent": "ResearchAgent/1.0 (academic evidence retriever)"},
        )

        if response.is_redirect:
            redirect_count += 1
            if redirect_count > max_redirects:
                raise ValueError(f"Too many redirects ({redirect_count}) for {url}")
            location = response.headers.get("location")
            if not location:
                raise ValueError("Redirect response missing Location header")
            # Resolve relative redirect URLs
            parsed_loc = urlparse(location)
            if not parsed_loc.netloc:
                from urllib.parse import urljoin

                current_url = urljoin(current_url, location)
            else:
                current_url = location
            continue

        response.raise_for_status()

        # Check content length
        content = bytearray()
        async for chunk in response.aiter_bytes():
            content.extend(chunk)
            if len(content) > max_size_bytes:
                content = content[:max_size_bytes]
                break

        text = content.decode("utf-8", errors="replace")
        content_hash = calculate_content_hash(text)
        return text, content_hash
