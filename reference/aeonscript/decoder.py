"""High-level AeonScript decoder.

Inverse of encoder.py:
    list[oligo DNA] → concatenated bytes → RS-decoded → tag-stripped → payload
"""

from __future__ import annotations

from typing import Iterable

from .error_correction import decode_with_ecc
from .physical import dna_to_bytes
from .scrambler import descramble
from .semantic import parse_tag, validate_tag_dict

DEFAULT_RS_PARITY = 32
DEFAULT_RS_BLOCK = 223


def decode_oligos(
    oligos: Iterable[str],
    *,
    rs_parity: int = DEFAULT_RS_PARITY,
    rs_block_size: int = DEFAULT_RS_BLOCK,
    return_metadata: bool = False,
) -> bytes | tuple[bytes, dict]:
    """Decode a list of AeonScript DNA oligos back to the original payload.

    Parameters
    ----------
    oligos : iterable of DNA strings
    rs_parity, rs_block_size : Reed-Solomon parameters (must match encoder)
    return_metadata : if True, also return the parsed semantic tag dict and
                      number of corrected errors.

    Returns
    -------
    bytes
        The decoded payload (excluding the semantic tag).
    Or, if return_metadata=True:
    tuple[bytes, dict]
        (payload, {"tag": {...}, "errors_corrected": int})
    """
    # ---- L1: oligos → bytes --------------------------------------------
    rs_encoded = bytearray()
    for oligo in oligos:
        rs_encoded.extend(dna_to_bytes(oligo))

    # ---- Descramble (inverse of encoder PRBS) -------------------------
    rs_encoded = descramble(bytes(rs_encoded))

    # ---- L4: Reed-Solomon decode ---------------------------------------
    tagged_data, n_errors = decode_with_ecc(
        rs_encoded, nsym=rs_parity, block_size=rs_block_size
    )

    # ---- L5: parse and strip semantic tag ------------------------------
    # The tag starts with the byte '|' (0x7C) and ends at the next '|'.
    if not tagged_data.startswith(b"|"):
        raise ValueError("Decoded stream does not start with a AeonScript tag '|'")
    end_idx = tagged_data.index(b"|", 1)
    tag_str = tagged_data[: end_idx + 1].decode("ascii")
    payload_start = end_idx + 1

    tag_dict = parse_tag(tag_str)
    ok, msg = validate_tag_dict(tag_dict)
    if not ok:
        raise ValueError(f"Invalid semantic tag: {msg}")

    declared_len = int(tag_dict["LEN"])
    raw_payload = tagged_data[payload_start:]

    # The RS encoder may have padded the last block with zeros; trust LEN.
    payload = raw_payload[:declared_len]

    if return_metadata:
        return payload, {"tag": tag_dict, "errors_corrected": n_errors}
    return payload
