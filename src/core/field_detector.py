from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from rapidfuzz import fuzz, process

from .locale_detector import LocaleInfo
from . import mappings as mappings_module


_MONTHS_ES = {
    "ene": "01", "enero": "01",
    "feb": "02", "febrero": "02",
    "mar": "03", "marzo": "03",
    "abr": "04", "abril": "04",
    "may": "05", "mayo": "05",
    "jun": "06", "junio": "06",
    "jul": "07", "julio": "07",
    "ago": "08", "agosto": "08",
    "sep": "09", "set": "09", "setiembre": "09", "sept": "09", "septiembre": "09",
    "oct": "10", "octubre": "10",
    "nov": "11", "noviembre": "11",
    "dic": "12", "diciembre": "12",
}


DATE_PATTERN = re.compile(
    r"(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})"
    r"|(\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2})"
    r"|(\d{1,2}[ \-](?:ene|feb|mar|abr|may|jun|jul|ago|sep|set|sept|oct|nov|dic)[a-z]*[ \-]\d{2,4})",
    re.IGNORECASE,
)

AMOUNT_PATTERN = re.compile(
    r"(?:[€$]|S/[\s]?|Gs\.[\s]?|R\$[\s]?|\$U[\s]?)?\s?-?\s?\d{1,3}(?:[.,]\d{3})*[.,]\d{2}",
)

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s\-]?)?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}"
)

URL_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+")

LABEL_VALUE_PATTERN = re.compile(
    r"^(?P<label>[A-Za-zÁÉÍÓÚÑáéíóúñ0-9\s\.\-°/ºª#]{2,80}?):\s+(?P<value>.+)$"
)

CLABE_PATTERN = re.compile(r"\b\d{18}\b")
IBAN_PATTERN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b")
ACCOUNT_PATTERN = re.compile(r"\b\d{10,20}\b|\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b")

VALUE_FIELDS = {"CLABE", "IBAN", "EMAIL", "TELEFONO", "WEB", "CUENTA", "BANCO"}
MX_BANKS = {
    "bbva", "bancomer", "banorte", "santander", "hsbc", "banregio",
    "banco azteca", "azteca", "banamex", "citibanamex", "scotiabank",
    "inbursa", "actinver", "mifel", "bancoppel", "banco del bajio",
    "banbajio", "banco base", "afirme", "banco ahorro", "bansefi",
    "banco paguitos", "bancomext", "banjercito", "banobras", "nafin",
    "banco Compartamos", "banco monex", "banco s3", "icbc", "bank of america",
    "jpmorgan", "deutsche", "barclays",
}
AR_BANKS = {
    "galicia", "macro", "santander rio", "santander argentina", "nacion",
    "nación", "provincia", "bbva argentina", "icbc argentina", "hsbc argentina",
    "patagonia", "comafi", "hipotecario", "ciudad", "supervielle",
    "banco de cordoba", "banco cordoba", "banco pampa",
}
BR_BANKS = {
    "itau", "itaú", "bradesco", "santander brasil", "banco do brasil",
    "caixa", "caixa economica", "nubank", "inter", "safra",
}
GENERIC_BANKS: set = set()

KNOWN_LABELS = {
    "total", "subtotal", "sub total", "sub-total",
    "iva", "igv", "icms", "tax", "impuesto",
    "rfc", "ruc", "cuit", "nit", "cnpj", "cpf", "nif", "rut", "ein",
    "factura", "invoice", "boleta", "nota", "recibo", "receipt", "comprobante",
    "fecha", "date", "emision", "emisión", "fecha emision", "fecha de emision",
    "fecha de emisión",
    "proveedor", "vendor", "supplier", "emisor", "emitter", "emisora",
    "cliente", "customer", "buyer", "comprador", "consumidor",
    "direccion", "dirección", "address", "domicilio",
    "telefono", "teléfono", "phone", "tel", "tel.", "celular",
    "email", "correo", "correo electronico", "correo electrónico", "e-mail",
    "nombre", "name", "razon social", "razón social", "denominacion", "denominación",
    "cfdi", "uuid", "folio", "serie", "folio fiscal",
    "cantidad", "quantity", "qty", "unidades", "uds",
    "precio", "price", "unitario", "precio unitario", "p.unit", "p unit",
    "descuento", "discount", "desc", "dto",
    "metodo pago", "método pago", "payment", "metodo de pago", "método de pago",
    "forma pago", "forma de pago",
    "moneda", "currency", "divisa",
    "tipo cambio", "exchange", "tipo de cambio",
    "importe", "monto", "amount", "valor", "suma", "cargo", "abono",
    "total a pagar", "total pagar", "importe total", "total final",
    "gran total", "total general", "neto", "neto a pagar",
    "receptor", "beneficiario", "destinatario", "favorecido",
    "a favor de", "recibido por", "recibi de", "recibí de",
    "nombre del receptor", "nombre del beneficiario",
    "nombre receptor", "nombre beneficiario",
    "cuenta", "no de cuenta", "no. de cuenta", "numero de cuenta",
    "número de cuenta", "cta", "cta.", "cuenta destino",
    "cuenta de destino", "cuenta origen", "cuenta de origen",
    "cuenta receptora", "cuenta beneficiaria", "cuenta del beneficiario",
    "clabe", "clabe interbancaria", "iban", "swift", "bic",
    "banco", "bank", "banco receptor", "banco destino",
    "banco de destino", "banco emisor", "banco origen",
    "banco de origen", "banco beneficiario",
    "institucion", "institución", "institucion bancaria",
    "entidad", "entidad financiera", "entidad bancaria",
    "monto recibido", "cantidad recibida", "importe recibido",
    "monto transferido", "cantidad transferida",
    "referencia", "ref", "ref.", "numero de operacion", "número de operación",
    "folio de operacion", "folio de operación", "no. de operacion",
    "concepto", "description", "descripcion", "descripción", "motivo",
    "observaciones", "notas", "comments",
    "transferencia", "deposito", "depósito", "cheque", "efectivo",
}

GENERIC_FIELDS = {
    "ARCHIVO": "ARCHIVO",
    "TIPO": "TIPO",
    "ESTADO": "ESTADO",
}


def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[\.\-_/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _squash_acronyms(text: str) -> str:
    """Collapse sequences of single letters separated by spaces: 'r f c' -> 'rfc'."""
    tokens = text.split()
    if len(tokens) < 2:
        return text
    out = []
    i = 0
    while i < len(tokens):
        if len(tokens[i]) == 1 and i + 1 < len(tokens) and len(tokens[i + 1]) == 1:
            buf = tokens[i]
            i += 1
            while i < len(tokens) and len(tokens[i]) == 1:
                buf += tokens[i]
                i += 1
            out.append(buf)
        else:
            out.append(tokens[i])
            i += 1
    return " ".join(out)


def _canonical_key(label: str) -> str:
    n = _normalize(label)
    n = re.sub(r"[^a-z0-9\s]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    n = _squash_acronyms(n)
    n = re.sub(r"\b(no|n|num|numero|numero|numero|numero)\b", "", n).strip()
    n = re.sub(r"\s+", " ", n)
    if not n:
        return "DESCONOCIDO"
    tokens = n.split()
    abbrev_map = {
        "rfc": "RFC", "ruc": "RUC", "cuit": "CUIT", "nit": "NIT",
        "cnpj": "CNPJ", "cpf": "CPF", "nif": "NIF", "rut": "RUT",
        "ein": "EIN", "cfdi": "CFDI", "uuid": "UUID",
        "iva": "IVA", "igv": "IGV", "icms": "ICMS",
        "subtotal": "SUBTOTAL",
        "dl": "DL",
    }
    if len(tokens) > 1:
        joined = "".join(tokens)
        if joined in abbrev_map:
            return abbrev_map[joined]
    out = []
    for tok in tokens:
        if tok in abbrev_map:
            out.append(abbrev_map[tok])
        else:
            out.append(tok.upper())
    key = " ".join(out) if len(out) > 1 else (out[0] if out else "DESCONOCIDO")
    return _apply_synonym_aliases(key)


_SYNONYM_ALIASES = {
    "BANCO DESTINO": "BANCO",
    "BANCO ORIGEN": "BANCO",
    "BANCO RECEPTOR": "BANCO",
    "BANCO BENEFICIARIO": "BANCO",
    "BANCO EMISOR": "BANCO",
    "INSTITUCION DESTINO": "BANCO",
    "INSTITUCION RECEPTORA": "BANCO",
    "INSTITUCION FINANCIERA": "BANCO",
    "ENTIDAD BANCARIA": "BANCO",
    "ENTIDAD RECEPTORA": "BANCO",
    "CUENTA DESTINO": "CUENTA",
    "CUENTA ORIGEN": "CUENTA",
    "CUENTA RECEPTORA": "CUENTA",
    "CUENTA BENEFICIARIA": "CUENTA",
    "CUENTA DEL BENEFICIARIO": "CUENTA",
    "CUENTA DE DESTINO": "CUENTA",
    "CUENTA DE ORIGEN": "CUENTA",
    "NOMBRE DEL RECEPTOR": "RECEPTOR",
    "NOMBRE RECEPTOR": "RECEPTOR",
    "NOMBRE DEL BENEFICIARIO": "RECEPTOR",
    "NOMBRE BENEFICIARIO": "RECEPTOR",
    "BENEFICIARIO": "RECEPTOR",
    "DESTINATARIO": "RECEPTOR",
    "FAVORECIDO": "RECEPTOR",
    "A FAVOR DE": "RECEPTOR",
    "RECIBI DE": "RECEPTOR",
    "RECIBIDO DE": "RECEPTOR",
    "MONTO RECIBIDO": "MONTO",
    "CANTIDAD RECIBIDA": "MONTO",
    "IMPORTE RECIBIDO": "MONTO",
    "MONTO TRANSFERIDO": "MONTO",
    "CANTIDAD TRANSFERIDA": "MONTO",
    "DEPOSITO POR": "MONTO",
    "DE OPERACION": "REFERENCIA",
    "DE OPERACION": "REFERENCIA",
    "NUMERO DE OPERACION": "REFERENCIA",
    "NO DE OPERACION": "REFERENCIA",
    "FOLIO DE OPERACION": "REFERENCIA",
    "FOLIO OPERACION": "REFERENCIA",
    "NO OPERACION": "REFERENCIA",
    "FECHA DE EMISION": "FECHA",
    "FECHA EMISION": "FECHA",
    "METODO DE PAGO": "METODO PAGO",
    "METODO PAGO": "METODO PAGO",
    "FORMA DE PAGO": "METODO PAGO",
    "FORMA PAGO": "METODO PAGO",
    "RAZON SOCIAL": "PROVEEDOR",
    "NOMBRE DEL PROVEEDOR": "PROVEEDOR",
    "NOMBRE DEL EMISOR": "PROVEEDOR",
    "CORREO ELECTRONICO": "EMAIL",
}


def _apply_synonym_aliases(canonical: str) -> str:
    return _SYNONYM_ALIASES.get(canonical, canonical)


def _is_known_label(label: str) -> bool:
    n = _normalize(label)
    n = re.sub(r"\b(no|n|num|numero|número)\b", "", n).strip()
    return n in KNOWN_LABELS


def _cluster_labels(labels: List[str], threshold: int = 82) -> Dict[str, str]:
    """Group similar labels together. Returns: raw_label -> canonical."""
    if not labels:
        return {}

    unique_labels = list({l.strip() for l in labels if l and l.strip()})
    canonical_for: Dict[str, str] = {}
    clusters: List[List[str]] = []

    for label in unique_labels:
        key = _canonical_key(label)
        assigned = False
        for cluster in clusters:
            rep = cluster[0]
            rep_key = _canonical_key(rep)
            if fuzz.token_set_ratio(key, rep_key) >= threshold or key == rep_key:
                cluster.append(label)
                canonical_for[label] = rep_key
                assigned = True
                break
        if not assigned:
            clusters.append([label])
            canonical_for[label] = key

    final: Dict[str, str] = {}
    for cluster in clusters:
        best = max(cluster, key=lambda x: (_known_label_score(x), len(x)))
        rep_key = _canonical_key(best)
        for lbl in cluster:
            final[lbl] = rep_key

    return final


def _known_label_score(label: str) -> int:
    return 1 if _is_known_label(label) else 0


def detect_fields_in_text(text: str, locale: LocaleInfo) -> Dict[str, str]:
    """Extract field->value pairs from a single receipt text.

    Strategy (revised):
      1. Run label-based detection FIRST so explicit labels like
         "Cuenta receptora:" win over regex-based detection of account numbers.
      2. Build a set of digit-only values already labeled, so we don't
         auto-create CLABE/CUENTA/TELEFONO that conflict with labeled data.
      3. Then run value-based detection (CLABE, IBAN, email, URL, bank
         names) only for fields that aren't already labeled and only for
         values that aren't already present.
      4. Add amount fallback only if no monetary labels exist.
    """
    fields: Dict[str, str] = {}
    if not text or not text.strip():
        return fields

    text_lower_norm = _normalize(text)

    # ── Phase 1: label-based detection ─────────────────────────────────
    for line in text.split("\n"):
        line = line.strip()
        if not line or len(line) < 3:
            continue
        m = LABEL_VALUE_PATTERN.match(line)
        if not m:
            continue
        label = m.group("label").strip()
        value = m.group("value").strip()
        if not value or len(value) > 200:
            continue
        if len(label) > 60:
            continue
        norm = _normalize(label)
        if not norm or norm in {"http", "https", "www", "tel", "email"}:
            continue
        fields[label] = value

    # ── Phase 2: collect already-labeled digit values to avoid duplicates
    labeled_digits: set = set()
    for v in fields.values():
        d = re.sub(r"\D", "", v)
        if d:
            labeled_digits.add(d)

    # ── Phase 3: value-based detection ────────────────────────────────
    # CLABE (18-digit) - only if no labeled field already has this value
    has_clabe_label = any("clabe" in _normalize(k) for k in fields)
    if not has_clabe_label:
        for clabe_match in CLABE_PATTERN.finditer(text):
            candidate = clabe_match.group(0).strip()
            if candidate in labeled_digits:
                continue
            fields["CLABE"] = candidate
            labeled_digits.add(candidate)
            break

    # IBAN
    if "IBAN" not in fields:
        iban_match = IBAN_PATTERN.search(text)
        if iban_match:
            iban_val = iban_match.group(0).strip()
            if not iban_val.isdigit():
                fields["IBAN"] = iban_val

    # Email
    if "EMAIL" not in fields:
        email_match = EMAIL_PATTERN.search(text)
        if email_match:
            fields["EMAIL"] = email_match.group(0).strip()

    # URL
    if "WEB" not in fields:
        url_match = URL_PATTERN.search(text)
        if url_match:
            fields["WEB"] = url_match.group(0).strip()

    # CUENTA (account number 10-20 digits) - skip if a "cuenta/cta" label
    # already exists OR if the number is already labeled elsewhere
    has_cuenta_label = any(
        _normalize(k).startswith("cuenta") or "cta" in _normalize(k).split()
        for k in fields
    )
    if not has_cuenta_label:
        for m in ACCOUNT_PATTERN.finditer(text):
            val = m.group(0).strip()
            if CLABE_PATTERN.fullmatch(val):
                continue
            digits = re.sub(r"\D", "", val)
            if digits in labeled_digits:
                continue
            fields["CUENTA"] = val
            labeled_digits.add(digits)
            break

    # TELEFONO - skip if the number is already labeled (avoid clabe-like matches)
    if "TELEFONO" not in fields:
        for m in re.finditer(
            r"(?<![\d-])(\+?\d{1,3}[\s\-]?)?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}(?![\d-])",
            text,
        ):
            candidate = m.group(0).strip()
            digits = re.sub(r"\D", "", candidate)
            if not (8 <= len(digits) <= 11):
                continue
            if digits in labeled_digits:
                continue
            fields["TELEFONO"] = candidate
            labeled_digits.add(digits)
            break

    # Banco (real bank names)
    bank_hits = []
    for bank in MX_BANKS | AR_BANKS | BR_BANKS:
        norm_bank = _normalize(bank)
        if norm_bank and len(norm_bank) >= 3 and norm_bank in text_lower_norm:
            bank_hits.append((len(norm_bank), bank))
    if bank_hits:
        bank_hits.sort(reverse=True)
        fields["BANCO"] = bank_hits[0][1].upper()

    # FECHA (regex-based) - only if not labeled
    if not any("fecha" in _normalize(k) for k in fields):
        date_match = DATE_PATTERN.search(text)
        if date_match:
            fields["FECHA"] = date_match.group(0).strip()

    # Amounts (for MONTO_DETECTADO fallback only)
    amount_matches = AMOUNT_PATTERN.findall(text)
    amounts = [a.strip() for a in amount_matches if a.strip()]

    label_lower_text = " ".join(fields.keys()).lower()
    has_total_label = any(
        kw in label_lower_text
        for kw in ("total", "subtotal", "iva", "importe", "monto", "valor")
    )
    if not has_total_label and amounts:
        fields["MONTO_DETECTADO"] = amounts[-1]

    return fields


def _merge_similar_canonicals(canonicals: List[str]) -> Dict[str, str]:
    """Second pass: merge canonicals that are very similar.

    Conservative merge rules:
      - Same after whitespace/case normalization (e.g., "SUB TOTAL" == "SUBTOTAL").
      - High token-set ratio (>= 92), strict same semantic field.
    """
    if len(canonicals) < 2:
        return {c: c for c in canonicals}
    canonical_set = sorted(set(canonicals), key=lambda x: (-len(x), x))
    parent: Dict[str, str] = {}
    for c in canonical_set:
        parent[c] = c

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            if len(ra) >= len(rb):
                parent[rb] = ra
            else:
                parent[ra] = rb

    def strict_whole_word_merge(a: str, b: str) -> bool:
        """True only if the longer one is the SHORTER one PLUS a few tokens AND the
        shorter is not a known standalone term that appears in many other fields."""
        ta = a.upper().split()
        tb = b.upper().split()
        if not ta or not tb:
            return False
        longer_t, shorter_t = (ta, tb) if len(ta) >= len(tb) else (tb, ta)
        if len(shorter_t) != 1 or len(longer_t) <= 2:
            return False
        shorter_tok = shorter_t[0]
        if shorter_tok in {"TOTAL", "SUBTOTAL", "IVA", "IMPORTE", "MONTO", "VALOR",
                            "FECHA", "RFC", "RUC", "CUIT", "NIT", "CLIENTE",
                            "PROVEEDOR", "RECEPTOR", "BANCO", "CUENTA"}:
            return False
        if shorter_tok in longer_t:
            return True
        return False

    for i, a in enumerate(canonical_set):
        for b in canonical_set[i + 1:]:
            a_norm = re.sub(r"\s+", "", a).upper()
            b_norm = re.sub(r"\s+", "", b).upper()
            if not a_norm or not b_norm:
                continue
            if a_norm == b_norm:
                union(a, b)
                continue
            if fuzz.token_set_ratio(a, b) >= 92 and fuzz.ratio(a, b) >= 85:
                union(a, b)
                continue
            if strict_whole_word_merge(a, b):
                union(a, b)

    result: Dict[str, str] = {}
    for c in canonical_set:
        result[c] = find(c)
    return result


def aggregate_fields(per_file_fields: List[Dict[str, str]], locale: LocaleInfo,
                     min_freq: int = 1) -> Tuple[List[str], List[Dict[str, str]]]:
    """Cluster fields across all files. Returns (ordered_columns, rows)."""
    saved = mappings_module.load_mappings()
    saved_columns: Dict[str, List[str]] = saved.get("columns", {})
    saved_canonicals = set(saved_columns.keys())

    all_raw_labels: List[str] = []
    for f in per_file_fields:
        all_raw_labels.extend(f.keys())

    cluster_map = _cluster_labels(all_raw_labels)

    raw_to_canonical: Dict[str, str] = dict(cluster_map)

    for raw_label, canonical in cluster_map.items():
        if canonical in saved_columns:
            for saved_alias in saved_columns[canonical]:
                if saved_alias != raw_label:
                    raw_to_canonical[saved_alias] = canonical

    canonical_to_values: Dict[str, List[str]] = defaultdict(list)
    for f in per_file_fields:
        for raw_label, value in f.items():
            canonical = raw_to_canonical.get(raw_label, _canonical_key(raw_label))
            canonical_to_values[canonical].append(value)

    initial_canonicals = list(canonical_to_values.keys())
    merge_map = _merge_similar_canonicals(initial_canonicals)

    final_canonical_to_values: Dict[str, List[str]] = defaultdict(list)
    for canonical, values in canonical_to_values.items():
        final = merge_map.get(canonical, canonical)
        final_canonical_to_values[final].extend(values)

    final_canonicals: List[str] = []
    for canonical, values in final_canonical_to_values.items():
        if len(values) >= min_freq:
            final_canonicals.append(canonical)

    final_canonicals.sort(key=lambda c: (
        0 if c in saved_canonicals else 1,
        -len(final_canonical_to_values[c]),
        c,
    ))

    for c in saved_canonicals:
        if c not in final_canonicals:
            final_canonicals.append(c)

    final_raw_to_canonical: Dict[str, str] = {}
    for raw_label, canonical in raw_to_canonical.items():
        final_canonical = merge_map.get(canonical, canonical)
        final_raw_to_canonical[raw_label] = final_canonical

    rows: List[Dict[str, str]] = []
    for f in per_file_fields:
        row: Dict[str, str] = {}
        for canonical in final_canonicals:
            value = ""
            for raw_label, val in f.items():
                if final_raw_to_canonical.get(raw_label, _canonical_key(raw_label)) == canonical:
                    value = val
                    break
            row[canonical] = value
        rows.append(row)

    new_mappings = {
        "locale": locale.code,
        "currency": locale.currency,
        "columns": {c: [lbl for lbl, can in final_raw_to_canonical.items() if can == c] for c in final_canonicals},
        "aliases": final_raw_to_canonical,
        "last_used": None,
    }
    mappings_module.save_mappings(new_mappings)

    return final_canonicals, rows


def build_master_columns(all_field_dicts: List[Dict[str, str]], locale: LocaleInfo,
                         min_freq: int = 1) -> Tuple[List[str], List[Dict[str, str]]]:
    """Main entry: receives all field dictionaries from all files, returns ordered columns + rows."""
    columns, rows = aggregate_fields(all_field_dicts, locale, min_freq=min_freq)

    priority_cols = ["ARCHIVO", "TIPO", "ESTADO"]
    for pc in reversed(priority_cols):
        if pc in columns:
            columns.remove(pc)
        columns.insert(0, pc)

    return columns, rows
