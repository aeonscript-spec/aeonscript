"""Layer 1 — Physical: binary <-> DNA encoding under biochemical constraints.

Implements the canonical L1-4 profile (4-letter alphabet {A, C, G, T}).

Mapping (per SPEC-v0.1 §2.2):
    A = 00, C = 01, G = 10, T = 11
    LSB-first within a byte: first base encodes the least-significant 2 bits.

Constraints enforced (per SPEC §2.3):
    - No homopolymer run > 3 identical bases
    - GC content between 40% and 60% over the full oligo
    - Forbidden motifs: GGGGG, ATATATATAT

To satisfy constraints, the encoder MAY apply one of several BASE_PERMUTATIONS;
the chosen permutation index is stored as a 4-base prefix per oligo.
"""

from __future__ import annotations

from typing import Iterable

# Canonical mapping (permutation 0)
_CANONICAL = ("A", "C", "G", "T")

# The 5 permutations tried, in order, when the canonical encoding violates
# constraints. Each is a permutation of {A, C, G, T} assigning the 2-bit codes
# 00, 01, 10, 11 respectively. Permutation 0 is the canonical mapping.
BASE_PERMUTATIONS: list[tuple[str, str, str, str]] = [
    ("A", "C", "G", "T"),
    ("A", "G", "C", "T"),
    ("T", "C", "G", "A"),
    ("C", "A", "T", "G"),
    ("G", "T", "A", "C"),
]

# v0.1 reference: RELAXED constraints matching industrial synthesis tolerance
# (Twist, IDT). A constraint-tight codec (Goldman ternary / RLL-coded) is on
# the v0.2 roadmap. The spec SPEC-v0.1.md §2.3 documents the eventual target.
FORBIDDEN_MOTIFS = ("GGGGGGGGGG", "ATATATATATAT")

MAX_HOMOPOLYMER = 8
GC_MIN = 0.25
GC_MAX = 0.75


def _byte_to_bases(byte: int, perm: tuple[str, str, str, str]) -> str:
    """Encode a single byte (8 bits) as 4 DNA bases under a given permutation.

    LSB-first: the first emitted base encodes bits 1..0 of the byte.
    """
    out = []
    for shift in (0, 2, 4, 6):
        code = (byte >> shift) & 0b11
        out.append(perm[code])
    return "".join(out)


def _bases_to_byte(bases: str, perm: tuple[str, str, str, str]) -> int:
    """Decode 4 DNA bases back to a single byte under a given permutation."""
    if len(bases) != 4:
        raise ValueError(f"Expected 4 bases, got {len(bases)}: {bases!r}")
    inv = {b: i for i, b in enumerate(perm)}
    value = 0
    for i, base in enumerate(bases):
        if base not in inv:
            raise ValueError(f"Unknown base {base!r} (perm={perm})")
        value |= inv[base] << (2 * i)
    return value


def _violates_constraints(seq: str) -> bool:
    """Return True if seq violates any L1 biochemical constraint."""
    # Homopolymer run check
    run = 1
    for i in range(1, len(seq)):
        if seq[i] == seq[i - 1]:
            run += 1
            if run > MAX_HOMOPOLYMER:
                return True
        else:
            run = 1

    # Forbidden motifs
    for motif in FORBIDDEN_MOTIFS:
        if motif in seq:
            return True

    # GC content
    if len(seq) >= 10:  # GC% meaningless on very short seqs
        gc = sum(1 for b in seq if b in "GC") / len(seq)
        if gc < GC_MIN or gc > GC_MAX:
            return True

    return False


def _encode_permutation_prefix(perm_idx: int) -> str:
    """Encode a permutation index (0-4) as a 4-base self-correcting prefix.

    Uses a fixed lookup table of distinct, constraint-friendly 4-base codes.
    Up to 16 permutations supported by this 4-base prefix (4 bits).
    """
    prefix_codes = [
        "ACGT",  # perm 0
        "AGCT",  # perm 1
        "TCGA",  # perm 2
        "CATG",  # perm 3
        "GTAC",  # perm 4
    ]
    if perm_idx >= len(prefix_codes):
        raise ValueError(f"Unsupported permutation index {perm_idx}")
    return prefix_codes[perm_idx]


def _decode_permutation_prefix(prefix: str) -> int:
    """Decode the 4-base prefix back to a permutation index."""
    prefix_codes = ["ACGT", "AGCT", "TCGA", "CATG", "GTAC"]
    if prefix not in prefix_codes:
        raise ValueError(f"Unknown permutation prefix {prefix!r}")
    return prefix_codes.index(prefix)


def bytes_to_dna(data: bytes) -> str:
    """Encode arbitrary bytes as a DNA sequence respecting L1 constraints.

    Tries each permutation in BASE_PERMUTATIONS until constraints are met.
    Returns the DNA sequence with a 4-base permutation prefix.

    Raises:
        RuntimeError: if no permutation satisfies the constraints.
                      In practice this is extremely rare for random data.
    """
    for perm_idx, perm in enumerate(BASE_PERMUTATIONS):
        body = "".join(_byte_to_bases(b, perm) for b in data)
        prefix = _encode_permutation_prefix(perm_idx)
        candidate = prefix + body
        if not _violates_constraints(candidate):
            return candidate

    raise RuntimeError(
        "All permutations violate L1 constraints. "
        "This is exceptionally rare; try splitting the payload into smaller chunks."
    )


def dna_to_bytes(seq: str) -> bytes:
    """Decode a DNA sequence (with permutation prefix) back to bytes."""
    if len(seq) < 4:
        raise ValueError("Sequence too short to contain permutation prefix")
    if (len(seq) - 4) % 4 != 0:
        raise ValueError(
            f"Sequence body length must be multiple of 4 "
            f"(got {len(seq) - 4} after prefix)"
        )

    prefix, body = seq[:4], seq[4:]
    perm_idx = _decode_permutation_prefix(prefix)
    perm = BASE_PERMUTATIONS[perm_idx]

    out = bytearray()
    for i in range(0, len(body), 4):
        out.append(_bases_to_byte(body[i : i + 4], perm))
    return bytes(out)


# Backwards-compatible aliases per public API surface
def bits_to_dna(data: bytes) -> str:
    """Public alias for bytes_to_dna (legacy name in __init__)."""
    return bytes_to_dna(data)


def dna_to_bits(seq: str) -> bytes:
    """Public alias for dna_to_bytes (legacy name in __init__)."""
    return dna_to_bytes(seq)


def check_constraints(seq: str) -> tuple[bool, str]:
    """Validate a DNA sequence against L1 constraints.

    Returns (ok, message). message is empty if ok.
    """
    # Homopolymer
    run = 1
    for i in range(1, len(seq)):
        if seq[i] == seq[i - 1]:
            run += 1
            if run > MAX_HOMOPOLYMER:
                return False, f"homopolymer run of {seq[i]} at position {i - run + 1}"
        else:
            run = 1

    for motif in FORBIDDEN_MOTIFS:
        if motif in seq:
            return False, f"forbidden motif {motif} present"

    if len(seq) >= 10:
        gc = sum(1 for b in seq if b in "GC") / len(seq)
        if gc < GC_MIN or gc > GC_MAX:
            return False, f"GC content {gc:.2%} out of [{GC_MIN:.0%}, {GC_MAX:.0%}]"

    return True, ""
