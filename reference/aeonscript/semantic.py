"""Layer 5 — Session: semantic tags.

Tags are ASCII strings of the form:
    |KEY1=VALUE1;KEY2=VALUE2;...|

They are themselves encoded as L1 DNA via aeonscript.physical.bytes_to_dna,
so they share the same constraint regime as data oligos.

Per SPEC-v0.1 §4.2, mandatory keys are:
    AEONSCRIPT, L1, L4, TYPE, LEN, ID
"""

from __future__ import annotations

MANDATORY_KEYS = ("AEONSCRIPT", "L1", "L4", "TYPE", "LEN", "ID")


def make_tag(
    *,
    spec_version: str = "0.1",
    l1_profile: str = "L1-4",
    l4_codec: str = "rs255-223",
    mime_type: str = "application/octet-stream",
    payload_len: int,
    block_id: str,
    **optional: str,
) -> str:
    """Build a AeonScript semantic tag string.

    Parameters
    ----------
    spec_version : AeonScript spec version (e.g. "0.1")
    l1_profile   : L1 alphabet profile, default "L1-4"
    l4_codec     : L4 error correction codec, default "rs255-223"
    mime_type    : MIME type of the payload
    payload_len  : Length in bytes of the decoded payload
    block_id     : Unique identifier for this block
    **optional   : Additional keys (TIER, ENCRYPT, COMPRESS, CHECKSUM, ...)
    """
    fields = {
        "AEONSCRIPT": spec_version,
        "L1": l1_profile,
        "L4": l4_codec,
        "TYPE": mime_type,
        "LEN": str(payload_len),
        "ID": block_id,
    }
    fields.update(optional)
    body = ";".join(f"{k}={v}" for k, v in fields.items())
    return f"|{body}|"


def parse_tag(tag: str) -> dict[str, str]:
    """Parse a tag string back into a dict.

    Raises ValueError on malformed input.
    """
    if not (tag.startswith("|") and tag.endswith("|")):
        raise ValueError(f"Tag must be wrapped in '|...|', got: {tag[:80]!r}")
    body = tag[1:-1]
    if not body:
        raise ValueError("Empty tag body")
    out: dict[str, str] = {}
    for pair in body.split(";"):
        if "=" not in pair:
            raise ValueError(f"Malformed tag field (no '='): {pair!r}")
        key, _, value = pair.partition("=")
        out[key] = value

    missing = [k for k in MANDATORY_KEYS if k not in out]
    if missing:
        raise ValueError(f"Tag missing mandatory keys: {missing}")

    return out


def validate_tag_dict(tag: dict[str, str]) -> tuple[bool, str]:
    """Validate the contents of a parsed tag against v0.1 requirements."""
    if tag.get("AEONSCRIPT") != "0.1":
        return False, f"Unsupported AEONSCRIPT version: {tag.get('AEONSCRIPT')!r}"
    if tag.get("L1") not in ("L1-4", "L1-5m", "L1-6"):
        return False, f"Unsupported L1 profile: {tag.get('L1')!r}"
    try:
        int(tag["LEN"])
    except (KeyError, ValueError):
        return False, "LEN must be a non-negative integer"
    return True, ""
