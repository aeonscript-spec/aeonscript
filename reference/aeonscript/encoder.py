"""High-level AeonScript encoder.

Pipeline (top-to-bottom):
    payload (bytes)
      → L5 semantic tag prepended
      → L4 Reed-Solomon error correction applied
      → L1 DNA encoding (with constraint-aware base permutation)
      → split into oligos of configured length

Each oligo is a self-contained, synthesizable DNA string.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Iterable

from .error_correction import encode_with_ecc
from .physical import bytes_to_dna
from .scrambler import scramble
from .semantic import make_tag

DEFAULT_OLIGO_LENGTH = 200  # bases; SPEC §2.4 recommendation
DEFAULT_RS_PARITY = 32  # SPEC §3.1
DEFAULT_RS_BLOCK = 223


_FORBIDDEN_TAG_CHARS = (";", "=", "|")


def _validate_tag_value(name: str, value: str) -> None:
    """Raise ValueError if `value` contains characters reserved by the L5 wire format."""
    bad = [c for c in _FORBIDDEN_TAG_CHARS if c in value]
    if bad:
        raise ValueError(
            f"L5 tag value for {name} contains reserved characters {bad!r}: "
            f"{value!r}. Per SPEC-v0.1 §4.5, the characters ';', '=', '|' "
            f"are not permitted in tag values (escape sequences reserved for v0.2)."
        )


def _blake3_or_sha256(data: bytes) -> str:
    """Return a hash of the data. Uses BLAKE3 if available, else SHA-256."""
    try:
        import blake3  # type: ignore

        return f"blake3:{blake3.blake3(data).hexdigest()}"
    except ImportError:
        return f"sha256:{hashlib.sha256(data).hexdigest()}"


def encode_bytes(
    data: bytes,
    *,
    mime_type: str = "application/octet-stream",
    block_id: str | None = None,
    oligo_length: int = DEFAULT_OLIGO_LENGTH,
    rs_parity: int = DEFAULT_RS_PARITY,
    rs_block_size: int = DEFAULT_RS_BLOCK,
    extra_tag_fields: dict[str, str] | None = None,
) -> list[str]:
    """Encode arbitrary bytes into a list of DNA oligos.

    Returns
    -------
    list[str]
        Each element is a DNA sequence (A/C/G/T) of approximately
        `oligo_length` bases, ready for synthesis.
    """
    if block_id is None:
        block_id = _blake3_or_sha256(data)[:24]  # short prefix

    # ---- L5: prepend semantic tag --------------------------------------
    # The L5 wire format uses ';' as the field separator and '=' as the
    # key/value separator. In v0.1 these characters are forbidden in any
    # value (escape sequences are reserved for v0.2). We reject loudly
    # rather than silently truncate — losing the 'charset=utf-8' part of a
    # MIME type would be a silent data corruption.
    _validate_tag_value("mime_type", mime_type)
    if extra_tag_fields:
        for k, v in extra_tag_fields.items():
            _validate_tag_value(f"extra_tag_fields[{k!r}]", v)

    tag = make_tag(
        mime_type=mime_type,
        payload_len=len(data),
        block_id=block_id,
        CHECKSUM=_blake3_or_sha256(data),
        **(extra_tag_fields or {}),
    )
    tagged = tag.encode("ascii") + data

    # ---- L4: Reed-Solomon error correction -----------------------------
    rs_encoded = encode_with_ecc(tagged, nsym=rs_parity, block_size=rs_block_size)

    # ---- Scrambler: uniformize byte distribution ----------------------
    rs_encoded = scramble(rs_encoded)

    # ---- L1: DNA encoding with constraint enforcement -----------------
    # We chunk the RS-encoded bytes so each resulting oligo fits oligo_length
    # bases (each byte = 4 bases, plus 4-base permutation prefix per oligo).
    bytes_per_oligo = (oligo_length - 4) // 4
    if bytes_per_oligo < 16:
        raise ValueError(f"oligo_length={oligo_length} too small")

    oligos = []
    for i in range(0, len(rs_encoded), bytes_per_oligo):
        chunk = rs_encoded[i : i + bytes_per_oligo]
        oligos.append(bytes_to_dna(chunk))

    return oligos


def encode_file(
    path: str | os.PathLike,
    *,
    mime_type: str | None = None,
    **kwargs,
) -> list[str]:
    """Encode a file from disk into DNA oligos."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)

    if mime_type is None:
        # Naive MIME guess from extension
        ext_map = {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".json": "application/json",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".pdf": "application/pdf",
            ".bin": "application/octet-stream",
        }
        mime_type = ext_map.get(p.suffix.lower(), "application/octet-stream")

    data = p.read_bytes()
    block_id = kwargs.pop("block_id", p.name)
    return encode_bytes(
        data,
        mime_type=mime_type,
        block_id=block_id,
        **kwargs,
    )
