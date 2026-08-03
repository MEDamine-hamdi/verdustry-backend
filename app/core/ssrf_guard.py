import ipaddress
import socket
from urllib.parse import urlparse


class SSRFError(Exception):
    pass


def _is_ip_blocked(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # can't parse -> block by default

    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
        return True

    # Cloud metadata endpoints (AWS/GCP/Azure/DigitalOcean)
    if ip_str == "169.254.169.254":
        return True

    return False


def validate_url_safe(url: str) -> None:
    """Raise SSRFError if the URL is unsafe to fetch server-side."""
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise SSRFError(f"Schéma non autorisé: {parsed.scheme!r}. Seuls http/https sont acceptés.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("URL invalide: hôte manquant.")

    if hostname.lower() in ("localhost",):
        raise SSRFError("Les adresses locales ne sont pas autorisées.")

    try:
        resolved_ips = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise SSRFError(f"Impossible de résoudre l'hôte: {hostname}")

    for family, _, _, _, sockaddr in resolved_ips:
        ip_str = sockaddr[0]
        if _is_ip_blocked(ip_str):
            raise SSRFError(f"L'hôte {hostname} pointe vers une adresse non autorisée ({ip_str}).")


def validate_db_host_safe(connection_url: str) -> None:
    """Raise SSRFError if the SQL connection URL host is unsafe."""
    parsed = urlparse(connection_url)
    hostname = parsed.hostname

    if not hostname:
        raise SSRFError("URL de connexion invalide: hôte manquant.")

    if hostname.lower() in ("localhost",):
        raise SSRFError("Les connexions vers localhost ne sont pas autorisées.")

    try:
        resolved_ips = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise SSRFError(f"Impossible de résoudre l'hôte: {hostname}")

    for family, _, _, _, sockaddr in resolved_ips:
        ip_str = sockaddr[0]
        if _is_ip_blocked(ip_str):
            raise SSRFError(f"L'hôte {hostname} pointe vers une adresse non autorisée ({ip_str}).")