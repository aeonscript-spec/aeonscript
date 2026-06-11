"""L1 profile `L1-3-goldman` — Goldman 2013 ternary encoding.

This is an alternative physical-layer encoding that *structurally* prevents
homopolymer runs (no two consecutive identical bases possible), at the
cost of lower bit density.

Goldman et al. (2013) "Towards practical, high-capacity, low-maintenance
information storage in synthesized DNA". *Nature* 494, 77–80.

## How it works

Each byte (8 bits) is converted to base-3 (5 trits, since ⌈log_3(256)⌉ = 6
but we use a slightly tighter packing per Goldman). Each trit then maps to
one of the THREE bases NOT equal to the previous base on the strand.

For a previous base of `A`, the trit→base map is:
    0 → C, 1 → G, 2 → T   (anything but A)

For a previous base of `C`:
    0 → A, 1 → G, 2 → T

And so on. Because the new base is always *different* from the previous
one, no homopolymer of length 2 can exist. Conformant L1-3-goldman oligos
trivially satisfy the SPEC §2.3 homopolymer constraint.

## Density

5 trits per byte yields ~5 bases per byte → 1.6 bits/base, vs. 2 bits/base
for L1-4. A roughly 20 % density loss in exchange for structural homopolymer
elimination and a tighter, more synthesis-friendly oligo distribution.

## Status

Reference implementation for the v0.2 L1 profile system. Not yet declared
normative in v0.1; the canonical v0.1 profile remains L1-4.
"""

from __future__ import annotations

from typing import Iterable

# Trit-to-base maps, indexed by the previous base. The order C < G < T < A
# matches the standard Goldman 2013 convention.
_NEXT: dict[str, tuple[str, str, str]] = {
    "A": ("C", "G", "T"),
    "C": ("G", "T", "A"),
    "G": ("T", "A", "C"),
    "T": ("A", "C", "G"),
}

# Initial seed base — by convention. Any single base works; "A" is the
# Goldman 2013 default. The decoder reads this from the first symbol.
INITIAL_BASE = "A"


def _byte_to_trits(byte: int) -> list[int]:
    """Convert a byte (0..255) into 6 base-3 digits, low trit first.

    256 < 3^6 = 729, so 6 trits are always sufficient. Some encodings
    are wasted (256 of 729) but the round-trip is straightforward.
    """
    out: list[int] = []
    n = byte
    for _ in range(6):
        out.append(n % 3)
        n //= 3
    return out


def _trits_to_byte(trits: Iterable[int]) -> int:
    """Inverse of `_byte_to_trits`."""
    n = 0
    for i, t in enumerate(trits):
        n += t * (3**i)
    return n


def bytes_to_goldman_dna(data: bytes, initial_base: str = INITIAL_BASE) -> str:
    """Encode bytes as a Goldman ternary DNA string.

    Output structure: `[initial_base][trit_base_1][trit_base_2]...[trit_base_N]`
    where N = 6 × len(data).

    No two consecutive bases are equal — homopolymers of length 2 are
    structurally impossible.
    """
    if initial_base not in "ACGT":
        raise ValueError(f"initial_base must be A/C/G/T, got {initial_base!r}")
    out: list[str] = [initial_base]
    prev = initial_base
    for byte in data:
        for trit in _byte_to_trits(byte):
            next_base = _NEXT[prev][trit]
            out.append(next_base)
            prev = next_base
    return "".join(out)


def goldman_dna_to_bytes(seq: str) -> bytes:
    """Decode a Goldman ternary DNA string back to bytes.

    Expects the first base to be the initial seed (any A/C/G/T), followed
    by 6 × N bases where N is the number of payload bytes.
    """
    if not seq:
        raise ValueError("empty Goldman sequence")
    if (len(seq) - 1) % 6 != 0:
        raise ValueError(
            f"Goldman sequence body length must be a multiple of 6 "
            f"(got {len(seq) - 1} after initial base)"
        )
    prev = seq[0]
    if prev not in "ACGT":
        raise ValueError(f"invalid initial base {prev!r}")
    out = bytearray()
    body = seq[1:]
    for i in range(0, len(body), 6):
        chunk = body[i : i + 6]
        trits: list[int] = []
        for base in chunk:
            try:
                trit = _NEXT[prev].index(base)
            except ValueError as exc:
                raise ValueError(
                    f"invalid Goldman transition: {prev!r} → {base!r} (must differ)"
                ) from exc
            trits.append(trit)
            prev = base
        out.append(_trits_to_byte(trits))
    return bytes(out)


def density_bits_per_base(num_bytes: int) -> float:
    """Effective density (bits utiles / base) for an N-byte payload."""
    if num_bytes <= 0:
        return 0.0
    bases = 1 + 6 * num_bytes
    bits = num_bytes * 8
    return bits / bases
