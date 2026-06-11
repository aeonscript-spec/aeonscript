"""Tests for the Goldman ternary L1 profile (`L1-3-goldman`)."""

from __future__ import annotations

import random

import pytest

from aeonscript.goldman import (
    bytes_to_goldman_dna,
    goldman_dna_to_bytes,
    density_bits_per_base,
)


def test_round_trip_simple():
    data = b"Hello AeonScript via Goldman 2013."
    seq = bytes_to_goldman_dna(data)
    assert all(c in "ACGT" for c in seq), f"non-ACGT chars in {seq!r}"
    decoded = goldman_dna_to_bytes(seq)
    assert decoded == data


def test_round_trip_random():
    rng = random.Random(7)
    for _ in range(30):
        n = rng.randint(0, 80)
        data = bytes(rng.randint(0, 255) for _ in range(n))
        seq = bytes_to_goldman_dna(data)
        assert goldman_dna_to_bytes(seq) == data


def test_no_homopolymer_pairs():
    """Goldman encoding structurally prevents adjacent identical bases."""
    rng = random.Random(0)
    for _ in range(50):
        n = rng.randint(1, 100)
        data = bytes(rng.randint(0, 255) for _ in range(n))
        seq = bytes_to_goldman_dna(data)
        for i in range(1, len(seq)):
            assert seq[i] != seq[i - 1], (
                f"adjacent identical bases at position {i} of {seq!r}"
            )


def test_different_initial_bases():
    data = b"x" * 8
    seqs = {b: bytes_to_goldman_dna(data, initial_base=b) for b in "ACGT"}
    # All four seeds give distinct strings (their first base differs)
    assert len({s[0] for s in seqs.values()}) == 4
    # All round-trip correctly
    for seq in seqs.values():
        assert goldman_dna_to_bytes(seq) == data


def test_density_under_2():
    """Goldman density is structurally below 2 bits/base (the L1-4 ceiling)."""
    for n in (1, 10, 100, 1000):
        density = density_bits_per_base(n)
        assert 0 < density < 2, f"unexpected density {density} for n={n}"


def test_rejects_invalid_transition():
    """Decoding must reject sequences with adjacent identical bases."""
    # 7 chars total = initial 'A' + 6-base body, all 'A' — pairwise identical
    with pytest.raises(ValueError, match="must differ"):
        goldman_dna_to_bytes("AAAAAAA")


def test_rejects_invalid_initial_base():
    with pytest.raises(ValueError, match="initial base"):
        goldman_dna_to_bytes("NACGTAC")  # N is not a base


def test_rejects_bad_length():
    with pytest.raises(ValueError, match="multiple of 6"):
        goldman_dna_to_bytes("ACGT")  # 4 body bases isn't a multiple of 6
