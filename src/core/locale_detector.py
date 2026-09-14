from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class LocaleInfo:
    code: str
    country: str
    currency: str
    currency_symbol: str
    tax_label: str
    tax_id_label: str
    invoice_label: str
    date_format: str

    def to_dict(self) -> Dict:
        return asdict(self)


_LOCALE_SIGNATURES = [
    {
        "code": "MX", "country": "México", "currency": "MXN", "currency_symbol": "$",
        "tax_label": "IVA", "tax_id_label": "RFC", "invoice_label": "Factura",
        "date_format": "DD/MM/YYYY",
        "patterns": [r"\bRFC\b", r"\bIVA\b", r"\bCFDI\b", r"\bMXN\b", r"\$[\d,]+\.\d{2}"],
    },
    {
        "code": "AR", "country": "Argentina", "currency": "ARS", "currency_symbol": "$",
        "tax_label": "IVA", "tax_id_label": "CUIT", "invoice_label": "Factura",
        "date_format": "DD/MM/YYYY",
        "patterns": [r"\bCUIT\b", r"\bAFIP\b", r"\bARS\b", r"\bCAE\b", r"\bIVA 21\b", r"\bIVA 10\.5\b"],
    },
    {
        "code": "BR", "country": "Brasil", "currency": "BRL", "currency_symbol": "R$",
        "tax_label": "ICMS", "tax_id_label": "CNPJ", "invoice_label": "Nota Fiscal",
        "date_format": "DD/MM/YYYY",
        "patterns": [r"\bCNPJ\b", r"\bCPF\b", r"\bICMS\b", r"\bNFe\b", r"R\$[\d\.,]+"],
    },
    {
        "code": "CL", "country": "Chile", "currency": "CLP", "currency_symbol": "$",
        "tax_label": "IVA", "tax_id_label": "RUT", "invoice_label": "Boleta",
        "date_format": "DD/MM/YYYY",
        "patterns": [r"\bRUT\b", r"\bSII\b", r"\bBoleta\b", r"\$\s*[\d\.]+"],
    },
    {
        "code": "CO", "country": "Colombia", "currency": "COP", "currency_symbol": "$",
        "tax_label": "IVA", "tax_id_label": "NIT", "invoice_label": "Factura",
        "date_format": "DD/MM/YYYY",
        "patterns": [r"\bNIT\b", r"\bDIAN\b", r"\bCOP\b", r"\$\s*[\d\.]+"],
    },
    {
        "code": "PE", "country": "Perú", "currency": "PEN", "currency_symbol": "S/",
        "tax_label": "IGV", "tax_id_label": "RUC", "invoice_label": "Boleta",
        "date_format": "DD/MM/YYYY",
        "patterns": [r"\bRUC\b", r"\bIGV\b", r"\bSUNAT\b", r"S/\s?[\d\.,]+", r"\bBoleta\b"],
    },
    {
        "code": "PY", "country": "Paraguay", "currency": "PYG", "currency_symbol": "Gs.",
        "tax_label": "IVA", "tax_id_label": "RUC", "invoice_label": "Factura",
        "date_format": "DD/MM/YYYY",
        "patterns": [r"\bRUC\b", r"\bGs\.\b", r"\bIVA 10\b", r"\bIVA 5\b", r"\bSET\b"],
    },
    {
        "code": "UY", "country": "Uruguay", "currency": "UYU", "currency_symbol": "$U",
        "tax_label": "IVA", "tax_id_label": "RUT", "invoice_label": "Factura",
        "date_format": "DD/MM/YYYY",
        "patterns": [r"\bRUT\b", r"\bDGI\b", r"\bUYU\b", r"\$U\s*[\d\.,]+"],
    },
    {
        "code": "US", "country": "Estados Unidos", "currency": "USD", "currency_symbol": "$",
        "tax_label": "Tax", "tax_id_label": "EIN", "invoice_label": "Invoice",
        "date_format": "MM/DD/YYYY",
        "patterns": [r"\bInvoice\b", r"\bEIN\b", r"\bUSD\b", r"\bSubtotal\b", r"\bTax\b"],
    },
    {
        "code": "ES", "country": "España", "currency": "EUR", "currency_symbol": "€",
        "tax_label": "IVA", "tax_id_label": "NIF", "invoice_label": "Factura",
        "date_format": "DD/MM/YYYY",
        "patterns": [r"\bNIF\b", r"\bCIF\b", r"\bEUR\b", r"\d+,\d{2}\s?€", r"€\s?[\d\.,]+"],
    },
]

_DEFAULT_LOCALE = LocaleInfo(
    code="MX", country="México", currency="MXN", currency_symbol="$",
    tax_label="IVA", tax_id_label="RFC", invoice_label="Factura",
    date_format="DD/MM/YYYY",
)


def detect_locale(texts: List[str]) -> LocaleInfo:
    """Detect the most probable locale from a list of text strings."""
    if not texts:
        return _DEFAULT_LOCALE

    combined = "\n".join(texts)
    scores: Counter = Counter()

    for sig in _LOCALE_SIGNATURES:
        score = 0
        for pattern in sig["patterns"]:
            matches = re.findall(pattern, combined, re.IGNORECASE)
            score += len(matches)
        scores[sig["code"]] = score

    if not scores or max(scores.values()) == 0:
        return _DEFAULT_LOCALE

    best_code, _ = scores.most_common(1)[0]
    for sig in _LOCALE_SIGNATURES:
        if sig["code"] == best_code:
            return LocaleInfo(
                code=sig["code"], country=sig["country"],
                currency=sig["currency"], currency_symbol=sig["currency_symbol"],
                tax_label=sig["tax_label"], tax_id_label=sig["tax_id_label"],
                invoice_label=sig["invoice_label"], date_format=sig["date_format"],
            )

    return _DEFAULT_LOCALE


def merge_locales(locales: List[LocaleInfo]) -> LocaleInfo:
    if not locales:
        return _DEFAULT_LOCALE
    if len(locales) == 1:
        return locales[0]

    codes = Counter(l.code for l in locales)
    most_common_code, _ = codes.most_common(1)[0]
    for l in locales:
        if l.code == most_common_code:
            return l
    return locales[0]
