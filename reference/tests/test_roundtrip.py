"""Round-trip integration tests for the AeonScript reference codec.

Verifies that encode → decode recovers the original bytes exactly,
and that Reed-Solomon corrects a realistic number of injected errors.
"""

from __future__ import annotations

import random

import pytest

from aeonscript import encode_bytes, decode_oligos
from aeonscript.physical import bytes_to_dna, dna_to_bytes, check_constraints
from aeonscript.error_correction import (
    rs_encode_msg,
    rs_decode_msg,
    encode_with_ecc,
    decode_with_ecc,
)


# ---------------------------------------------------------------------------
# L1 — physical layer
# ---------------------------------------------------------------------------


def test_l1_roundtrip_simple():
    data = b"Hello AeonScript world."
    seq = bytes_to_dna(data)
    assert all(c in "ACGT" for c in seq)
    assert dna_to_bytes(seq) == data


def test_l1_roundtrip_random():
    rng = random.Random(42)
    for _ in range(20):
        size = rng.randint(1, 50)
        data = bytes(rng.randint(0, 255) for _ in range(size))
        seq = bytes_to_dna(data)
        assert dna_to_bytes(seq) == data


def test_l1_constraints_respected():
    rng = random.Random(0)
    for _ in range(20):
        data = bytes(rng.randint(0, 255) for _ in range(30))
        seq = bytes_to_dna(data)
        ok, msg = check_constraints(seq)
        assert ok, f"constraints violated: {msg} for seq={seq}"


# ---------------------------------------------------------------------------
# L4 — Reed-Solomon
# ---------------------------------------------------------------------------


def test_rs_no_errors():
    data = bytes(range(100))
    codeword = rs_encode_msg(data, nsym=20)
    decoded, n_err = rs_decode_msg(codeword, nsym=20)
    assert decoded == data
    assert n_err == 0


def test_rs_corrects_few_errors():
    data = bytes(range(100))
    codeword = bytearray(rs_encode_msg(data, nsym=20))
    # Corrupt up to 10 bytes (RS can correct nsym/2 = 10)
    rng = random.Random(123)
    positions = rng.sample(range(len(codeword)), 8)
    for p in positions:
        codeword[p] ^= rng.randint(1, 255)
    decoded, n_err = rs_decode_msg(bytes(codeword), nsym=20)
    assert decoded == data
    assert n_err == 8


def test_rs_blocked_encode_decode():
    data = bytes(range(256)) * 3  # 768 bytes
    encoded = encode_with_ecc(data, nsym=32, block_size=223)
    decoded, n_err = decode_with_ecc(encoded, nsym=32, block_size=223)
    assert decoded[: len(data)] == data
    assert n_err == 0


# ---------------------------------------------------------------------------
# End-to-end (L1 + L4 + L5)
# ---------------------------------------------------------------------------


def test_end_to_end_small_text():
    original = b"AeonScript round-trip test of a small payload."
    oligos = encode_bytes(original, mime_type="text/plain", block_id="t1")
    decoded = decode_oligos(oligos)
    assert decoded == original


def test_end_to_end_returns_metadata():
    original = b"With metadata."
    oligos = encode_bytes(original, mime_type="text/plain", block_id="meta-test")
    decoded, meta = decode_oligos(oligos, return_metadata=True)
    assert decoded == original
    assert meta["tag"]["AEONSCRIPT"] == "0.1"
    assert meta["tag"]["TYPE"] == "text/plain"
    assert meta["tag"]["ID"] == "meta-test"
    assert int(meta["tag"]["LEN"]) == len(original)


def test_end_to_end_binary_payload():
    rng = random.Random(7)
    original = bytes(rng.randint(0, 255) for _ in range(500))
    oligos = encode_bytes(original, mime_type="application/octet-stream")
    decoded = decode_oligos(oligos)
    assert decoded == original


def test_end_to_end_oligos_are_valid_dna():
    original = b"x" * 200
    oligos = encode_bytes(original)
    for o in oligos:
        assert all(c in "ACGT" for c in o), f"Non-ACGT base in oligo: {o!r}"


def test_oligo_length_bound():
    original = b"y" * 600
    oligos = encode_bytes(original, oligo_length=200)
    for o in oligos[:-1]:  # last one may be shorter
        assert len(o) <= 200, f"Oligo too long: {len(o)} bases"


if __name__ == "__main__":
    # Allow `python tests/test_roundtrip.py`
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
