"""Layer 4 — Transport: Reed-Solomon error correction.

v0.1 uses the `reedsolo` library (BSD-3, well-tested, used in production by
QR-code decoders and CCSDS deep-space links). A from-scratch GF(256) +
Berlekamp-Massey + Forney implementation was attempted earlier; we chose
correctness-via-proven-library over the aesthetic of zero dependencies.

Default parameters per SPEC-v0.1 §3.1:
    n=255, k=223, parity=32 → corrects up to 16 byte errors per codeword.
"""

from __future__ import annotations

from reedsolo import RSCodec, ReedSolomonError

DEFAULT_NSYM = 32
DEFAULT_BLOCK = 223


class DecodeError(Exception):
    """Raised when Reed-Solomon decoding fails (too many errors)."""


def _codec(nsym: int) -> RSCodec:
    """Return an RSCodec configured with the given parity count."""
    return RSCodec(nsym=nsym, fcr=0, prim=0x11D, generator=2, c_exp=8)


def rs_encode_msg(msg_in: bytes, nsym: int = DEFAULT_NSYM) -> bytes:
    """Encode bytes with `nsym` parity symbols.

    Returns a systematic codeword: original bytes + nsym parity bytes.
    """
    if len(msg_in) + nsym > 255:
        raise ValueError(
            f"Message too long: len(msg)+nsym={len(msg_in) + nsym} > 255"
        )
    return bytes(_codec(nsym).encode(msg_in))


def rs_decode_msg(codeword: bytes, nsym: int = DEFAULT_NSYM) -> tuple[bytes, int]:
    """Decode a Reed-Solomon codeword.

    Returns (corrected_message_bytes, n_errors_corrected).
    Raises DecodeError if uncorrectable.
    """
    try:
        decoded, _full, errata = _codec(nsym).decode(codeword)
    except ReedSolomonError as exc:
        raise DecodeError(str(exc)) from exc
    return bytes(decoded), len(errata)


# ---------------------------------------------------------------------------
# Block-level encode/decode
# ---------------------------------------------------------------------------


def encode_with_ecc(
    data: bytes,
    nsym: int = DEFAULT_NSYM,
    block_size: int = DEFAULT_BLOCK,
) -> bytes:
    """Split data into RS blocks of size `block_size` and encode each.

    The final block is zero-padded to `block_size` if needed. The L5 LEN
    field is responsible for tracking the original payload length so the
    decoder can strip the padding.
    """
    out = bytearray()
    for i in range(0, len(data), block_size):
        chunk = data[i : i + block_size]
        if len(chunk) < block_size:
            chunk = chunk + bytes([0] * (block_size - len(chunk)))
        out.extend(rs_encode_msg(chunk, nsym))
    return bytes(out)


def decode_with_ecc(
    data: bytes,
    nsym: int = DEFAULT_NSYM,
    block_size: int = DEFAULT_BLOCK,
) -> tuple[bytes, int]:
    """Decode RS-encoded data, returning (payload, total_errors_corrected).

    The returned payload includes any zero-padding from the last block;
    the caller (decoder.py) uses the L5 LEN field to trim it.
    """
    full_block = block_size + nsym
    if len(data) % full_block != 0:
        raise ValueError(
            f"Data length {len(data)} not a multiple of full block size {full_block}"
        )

    out = bytearray()
    total_errors = 0
    for i in range(0, len(data), full_block):
        codeword = data[i : i + full_block]
        msg, n_errs = rs_decode_msg(codeword, nsym)
        out.extend(msg)
        total_errors += n_errs
    return bytes(out), total_errors
