"""
Entity Resolution across Statutes, Courts, Regulators, and Sectors.
"""

from typing import Dict, Optional


CANONICAL_AUTHORITY_ALIASES: Dict[str, str] = {
    "ftc": "US Federal Trade Commission (FTC)",
    "federal trade commission": "US Federal Trade Commission (FTC)",
    "hhs ocr": "US HHS Office for Civil Rights (OCR)",
    "cppa": "California Privacy Protection Agency (CalPrivacy)",
    "calprivacy": "California Privacy Protection Agency (CalPrivacy)",
    "opc": "Office of the Privacy Commissioner of Canada (OPC)",
    "cai": "Commission d'accès à l'information du Québec (CAI)",
    "ipc ontario": "Information and Privacy Commissioner of Ontario (IPC)",
    "cnil": "Commission Nationale de l'Informatique et des Libertés (CNIL)",
    "bfdi": "Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI)",
    "edpb": "European Data Protection Board (EDPB)",
    "edps": "European Data Protection Supervisor (EDPS)",
    "cjeu": "Court of Justice of the European Union (CJEU)",
    "dpc ireland": "Data Protection Commission (DPC Ireland)",
    "garante": "Garante per la protezione dei dati personali (Italy)",
    "aepd": "Agencia Española de Protección de Datos (AEPD)",
}


def resolve_authority_name(raw_name: str) -> str:
    """Resolve an authority alias or abbreviation to its canonical name."""
    key = (raw_name or "").strip().lower()
    return CANONICAL_AUTHORITY_ALIASES.get(key, (raw_name or "").strip())


__all__ = ["CANONICAL_AUTHORITY_ALIASES", "resolve_authority_name"]
