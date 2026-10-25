"""Validation for untrusted regulatory sources and their document contents."""
import html
import ipaddress
import re
import socket
from urllib.parse import urlsplit


class RegulatorySourceSecurityGuard:
    """Reject unsafe source addresses and mark document instructions as inert.

    Fetchers must revalidate redirects and pin connections to validated addresses
    to prevent DNS rebinding between validation and connection establishment.
    Sanitized documents remain untrusted data, never system instructions.
    """

    @staticmethod
    def validate_source_url(url, allowed_domains=None):
        if not isinstance(url, str) or any(ord(c) <= 32 for c in url) or "\\" in url:
            raise ValueError("Invalid source URL")
        try:
            parsed = urlsplit(url)
            host = (parsed.hostname or "").rstrip(".").encode("idna").decode().lower()
            port = parsed.port
        except (ValueError, UnicodeError) as exc:
            raise ValueError("Invalid source URL") from exc
        if parsed.scheme.lower() not in {"http", "https"} or not host:
            raise ValueError("HTTP or HTTPS source required")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("Source credentials are prohibited")
        if host == "localhost" or host.endswith(".localhost"):
            raise ValueError("Local sources are prohibited")
        if allowed_domains is not None:
            if isinstance(allowed_domains, str):
                allowed_domains = [allowed_domains]
            domains = {d.rstrip(".").encode("idna").decode().lower() for d in allowed_domains}
            if not any(host == d or host.endswith("." + d) for d in domains if d):
                raise ValueError("Source domain is not allowed")
        try:
            addresses = [ipaddress.ip_address(host)]
        except ValueError:
            try:
                addresses = [ipaddress.ip_address(item[4][0]) for item in
                             socket.getaddrinfo(host, port or (443 if parsed.scheme == "https" else 80),
                                                type=socket.SOCK_STREAM)]
            except (OSError, ValueError) as exc:
                raise ValueError("Source host could not be safely resolved") from exc
        if not addresses or any(not address.is_global or
                                (address.version == 6 and address.ipv4_mapped is not None
                                 and not address.ipv4_mapped.is_global)
                                for address in addresses):
            raise ValueError("Non-public source addresses are prohibited")
        return url

    @staticmethod
    def sanitize_document_text(raw_text, max_bytes=5_000_000):
        """Return {text, security_flags}; replace detected instructions with markers."""
        if not isinstance(raw_text, str):
            raise TypeError("Document text must be a string")
        if max_bytes < 0 or len(raw_text.encode("utf-8")) > max_bytes:
            raise ValueError("Document exceeds byte size limit")
        text = html.unescape(raw_text)
        patterns = (
            ("script", r"<\s*script\b[^>]*>.*?<\s*/\s*script\s*>|<\s*/?\s*script\b[^>]*>"),
            ("ignore_previous_instructions", r"\bignore\s+(?:all\s+)?previous\s+instructions\b"),
            ("system_prompt", r"\bsystem\s+prompt\s*:"),
            ("execute_command", r"\bexecute\s+command\b"),
            ("production_without_review", r"\bpromote\s+to\s+production\s+without\s+review\b"),
        )
        flags = []
        for flag, pattern in patterns:
            text, count = re.subn(pattern, "[UNTRUSTED CONTENT REMOVED]", text,
                                  flags=re.IGNORECASE | re.DOTALL)
            if count:
                flags.append(flag)
        return {"text": text, "security_flags": flags}
